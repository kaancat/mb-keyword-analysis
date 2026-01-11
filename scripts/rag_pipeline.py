"""
RAG pipeline for Monday Brew Google Ads KB.

Unifies the previous build/ingest scripts into a single source of truth with:
- semantic chunking that respects sections and sentence boundaries
- heuristic metadata enrichment (topic, subtopic, content_type, relevance)
- lightweight deduplication of overlapping/near-identical chunks
- priority weighting for agency-specific methodology vs generic course material
- reusable functions for full rebuilds and incremental adds

No external APIs are used; everything relies on local processing and Chroma's
default MiniLM embeddings.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import uuid
from dataclasses import dataclass, asdict
from typing import Iterable, List, Dict, Tuple

import chromadb


# ---- Paths & constants ----------------------------------------------------

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
KB_ROOT = os.path.join(BASE_DIR, "knowledge_base")
TRANSCRIPT_DIR = os.path.join(KB_ROOT, "transcripts")
DATA_EXAMPLES_DIR = os.path.join(KB_ROOT, "Data Examples")
BACKEND_KB_DIR = os.path.join(BASE_DIR, "backend", "knowledge_base")
EXTRACTED_JSON = os.path.join(BACKEND_KB_DIR, "extracted_raw.json")
CHROMA_PATH = os.path.join(BACKEND_KB_DIR, "chroma_db")
COLLECTION_NAME = "agency_knowledge"

# target ~200-500 tokens => roughly 150-380 words
MIN_WORDS = 120
TARGET_WORDS = 260
MAX_WORDS = 380


# ---- Data containers ------------------------------------------------------

@dataclass
class Chunk:
    text: str
    metadata: Dict[str, object]
    id: str


# ---- Text utilities -------------------------------------------------------


def slugify(name: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-").lower()
    return base or "chunk"


def split_sections(text: str) -> List[Tuple[str | None, str]]:
    """Split by headings (numbers, hashes) while keeping section title."""
    lines = text.splitlines()
    sections: List[Tuple[str | None, List[str]]] = []
    current_title = None
    current_lines: List[str] = []
    heading_pattern = re.compile(r"^(#|\d+\.\d+|Section\s+\d+)")

    for line in lines:
        if heading_pattern.match(line.strip()):
            if current_lines:
                sections.append((current_title, "\n".join(current_lines).strip()))
            current_title = line.strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_title, "\n".join(current_lines).strip()))

    if not sections:
        return [(None, text)]
    return sections


def sentence_split(text: str) -> List[str]:
    # Light-weight sentence splitter that avoids splitting on decimals/URLs.
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text)
    sentences = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        # Split on paragraph breaks to respect boundaries
        for sub in re.split(r"\n{2,}", p):
            sub = sub.strip()
            if sub:
                sentences.append(sub)
    return sentences


def extract_highlights(sentences: List[str]) -> List[str]:
    keywords = ("always", "never", "avoid", "must", "should", "rule", "best practice", "warning")
    highlights = []
    for s in sentences:
        lower = s.lower()
        if any(k in lower for k in keywords):
            highlights.append(s.strip())
    return highlights[:6]  # keep concise


def chunk_sentences(sentences: List[str]) -> List[List[str]]:
    chunks: List[List[str]] = []
    buffer: List[str] = []
    word_count = 0

    for sent in sentences:
        words = len(sent.split())
        if word_count + words > MAX_WORDS and buffer:
            chunks.append(buffer)
            buffer = []
            word_count = 0

        buffer.append(sent)
        word_count += words

        if word_count >= TARGET_WORDS:
            chunks.append(buffer)
            buffer = []
            word_count = 0

    if buffer and len(buffer) > 0:
        chunks.append(buffer)
    return [c for c in chunks if sum(len(s.split()) for s in c) >= MIN_WORDS]


def build_chunk_text(section_title: str | None, sentences: List[str], source: str) -> str:
    highlights = extract_highlights(sentences)
    body = " ".join(sentences)
    header = f"Source: {source}"
    if section_title:
        header += f" | Section: {section_title}"
    if highlights:
        highlight_text = "\n".join(f"- {h}" for h in highlights)
        return f"{header}\nHighlights:\n{highlight_text}\nContext: {body}"
    return f"{header}\n{body}"


# ---- Metadata inference ---------------------------------------------------

TOPIC_KEYWORDS = {
    "match": "keyword_match_types",
    "phrase": "keyword_match_types",
    "broad": "keyword_match_types",
    "exact": "keyword_match_types",
    "campaign": "campaign_structure",
    "ad group": "ad_group_structure",
    "rsa": "ad_copy",
    "headline": "ad_copy",
    "description": "ad_copy",
    "negative": "negative_keywords",
    "search term": "search_terms",
    "n-gram": "search_terms",
    "quality score": "quality_score",
    "auction": "bidding",
    "bidding": "bidding",
    "pmax": "performance_max",
    "shopping": "performance_max",
    "conversion": "measurement",
    "tracking": "measurement",
    "geo": "geo_strategy",
    "location": "geo_strategy",
    "budget": "budgeting",
    "naming": "naming_conventions",
}


def infer_topic(text: str, filename: str) -> Tuple[str, str | None, List[str]]:
    lower = text.lower()
    topic = "general_google_ads"
    subtopic = None
    tags = []

    for key, value in TOPIC_KEYWORDS.items():
        if key in lower:
            topic = value
            tags.append(value)
            if key in ("broad", "phrase", "exact"):
                subtopic = key + "_match"
    if "spacefinder" in lower or "spacefinder" in filename.lower():
        tags.append("spacefinder")
        topic = topic or "case_study"
    return topic, subtopic, sorted(set(tags))


def infer_content_type(text: str, source_kind: str) -> str:
    lower = text.lower()
    if source_kind == "case_study":
        return "case_study"
    if source_kind == "agency":
        return "methodology"
    if any(w in lower for w in ("never", "avoid", "warning")):
        return "warning"
    if "example" in lower or "for example" in lower:
        return "example"
    if "best practice" in lower or "should" in lower or "rule" in lower:
        return "best_practice"
    return "methodology"


def infer_difficulty(filename: str, source_kind: str) -> str:
    if source_kind == "agency":
        return "intermediate"
    if source_kind == "case_study":
        return "advanced"
    # rough guess from module number if present
    match = re.match(r"(\d+)\.", os.path.basename(filename))
    if match and int(match.group(1)) <= 3:
        return "beginner"
    return "intermediate"


def infer_relevance(source_kind: str) -> float:
    return {"agency": 0.95, "case_study": 0.9, "course": 0.65}.get(source_kind, 0.6)


# ---- Deduplication --------------------------------------------------------


def fingerprint(text: str) -> set:
    tokens = re.findall(r"\w+", text.lower())
    shingles = [" ".join(tokens[i:i + 5]) for i in range(max(len(tokens) - 4, 1))]
    return set(shingles)


def dedupe_chunks(chunks: List[Chunk], threshold: float = 0.9) -> List[Chunk]:
    kept: List[Chunk] = []
    fp_list: List[set] = []
    for chunk in chunks:
        fp = fingerprint(chunk.text)
        duplicate = False
        for other_fp in fp_list:
            if not other_fp:
                continue
            inter = len(fp & other_fp)
            union = len(fp | other_fp) or 1
            sim = inter / union
            if sim >= threshold:
                duplicate = True
                break
        if not duplicate:
            kept.append(chunk)
            fp_list.append(fp)
    return kept


# ---- Loaders --------------------------------------------------------------


def load_transcript_chunks() -> List[Chunk]:
    chunks: List[Chunk] = []
    files = []
    for root, _, filenames in os.walk(TRANSCRIPT_DIR):
        for name in filenames:
            if name.lower().endswith(".txt"):
                files.append(os.path.join(root, name))

    for path in sorted(files):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            raw = f.read()
        sections = split_sections(raw)
        for section_title, section_text in sections:
            sentences = sentence_split(section_text)
            for sent_block in chunk_sentences(sentences):
                topic, subtopic, tags = infer_topic(" ".join(sent_block), os.path.basename(path))
                source_kind = "course"
                metadata = {
                    "source": os.path.basename(path),
                    "section": section_title,
                    "topic": topic,
                    "subtopic": subtopic,
                    "content_type": infer_content_type(" ".join(sent_block), source_kind),
                    "difficulty": infer_difficulty(path, source_kind),
                    "relevance_score": infer_relevance(source_kind),
                    "tags": tags or [topic],
                    "source_kind": source_kind,
                }
                text = build_chunk_text(section_title, sent_block, os.path.basename(path))
                chunk_id = f"{slugify(os.path.basename(path))}-{uuid.uuid4().hex[:8]}"
                chunks.append(Chunk(text=text, metadata=metadata, id=chunk_id))
    return chunks


def load_agency_md_chunks() -> List[Chunk]:
    md_files = [
        "keyword research rag.md",
        "RAG FROM TRANSCRIPT 1.md",
        "RAG FROM TRANSCRIPT 2.md",
    ]
    chunks: List[Chunk] = []
    for name in md_files:
        path = os.path.join(DATA_EXAMPLES_DIR, name)
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            raw = f.read()
        sections = split_sections(raw)
        for section_title, section_text in sections:
            sentences = sentence_split(section_text)
            for sent_block in chunk_sentences(sentences):
                topic, subtopic, tags = infer_topic(" ".join(sent_block), name)
                source_kind = "agency"
                metadata = {
                    "source": name,
                    "section": section_title,
                    "topic": topic,
                    "subtopic": subtopic,
                    "content_type": "methodology",
                    "difficulty": "intermediate",
                    "relevance_score": infer_relevance(source_kind),
                    "tags": tags or [topic],
                    "source_kind": source_kind,
                    "priority": 2,
                }
                text = build_chunk_text(section_title, sent_block, name)
                chunk_id = f"{slugify(name)}-{uuid.uuid4().hex[:8]}"
                chunks.append(Chunk(text=text, metadata=metadata, id=chunk_id))
    return chunks


def load_case_study_chunks() -> List[Chunk]:
    chunks: List[Chunk] = []
    if not os.path.exists(EXTRACTED_JSON):
        return chunks
    with open(EXTRACTED_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data.get("case_studies", []):
        filename = item.get("file", "case_study")
        source_kind = "case_study"
        base_meta = {
            "source": filename,
            "content_type": "case_study",
            "topic": "campaign_structure",
            "subtopic": "case_study",
            "difficulty": "advanced",
            "relevance_score": infer_relevance(source_kind),
            "tags": ["case_study", slugify(filename)],
            "source_kind": source_kind,
            "priority": 2,
        }

        parts = [f"CASE STUDY: {filename}"]
        match_stats = item.get("match_type_stats")
        if match_stats:
            parts.append(f"Match Type Strategy: {json.dumps(match_stats)}")
        naming = item.get("naming_samples") or []
        if naming:
            parts.append("Naming samples: " + "; ".join(naming))

        for row in item.get("sample_rows", [])[:50]:
            filtered = {k: v for k, v in row.items() if v not in ("nan", None, "-")}
            if filtered:
                parts.append("Example: " + json.dumps(filtered))

        full_text = "\n".join(parts)
        sentences = sentence_split(full_text)
        for sent_block in chunk_sentences(sentences):
            text = build_chunk_text("Case Study", sent_block, filename)
            chunk_id = f"case-{slugify(filename)}-{uuid.uuid4().hex[:8]}"
            chunks.append(Chunk(text=text, metadata=base_meta, id=chunk_id))
    return chunks


def load_audit_rule_chunks() -> List[Chunk]:
    chunks: List[Chunk] = []
    if not os.path.exists(EXTRACTED_JSON):
        return chunks
    with open(EXTRACTED_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    for item in data.get("audits", []):
        filename = item.get("file", "audit")
        for rule in item.get("extracted_rules", []):
            text = f"Audit Rule from {filename}: {rule}"
            metadata = {
                "source": filename,
                "topic": "audit_rules",
                "subtopic": None,
                "content_type": "warning" if "never" in rule.lower() else "best_practice",
                "difficulty": "intermediate",
                "relevance_score": 0.9,
                "tags": ["audit", "rule"],
                "source_kind": "agency",
                "priority": 2,
            }
            chunk_id = f"audit-{slugify(filename)}-{uuid.uuid4().hex[:8]}"
            chunks.append(Chunk(text=text, metadata=metadata, id=chunk_id))
    return chunks


# ---- Pipeline core --------------------------------------------------------


class RAGPipeline:
    def __init__(self, chroma_path: str = CHROMA_PATH, collection: str = COLLECTION_NAME):
        self.chroma_path = chroma_path
        self.collection_name = collection
        self.client = chromadb.PersistentClient(path=self.chroma_path)
        self.collection = self.client.get_or_create_collection(name=self.collection_name)

    def rebuild(self) -> int:
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        self.collection = self.client.create_collection(self.collection_name)

        chunks = []
        chunks.extend(load_agency_md_chunks())
        chunks.extend(load_case_study_chunks())
        chunks.extend(load_audit_rule_chunks())
        chunks.extend(load_transcript_chunks())

        print(f"Collected {len(chunks)} raw chunks; deduplicating...")
        unique_chunks = dedupe_chunks(chunks)
        print(f"{len(unique_chunks)} chunks after dedupe")
        self._persist(unique_chunks)
        return len(unique_chunks)

    def add_file(self, path: str) -> int:
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        ext = os.path.splitext(path)[1].lower()
        source_kind = "agency" if DATA_EXAMPLES_DIR in os.path.abspath(path) else "course"

        if ext in (".txt", ".md"):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                raw = f.read()
            sections = split_sections(raw)
            chunks: List[Chunk] = []
            for section_title, section_text in sections:
                sentences = sentence_split(section_text)
                for sent_block in chunk_sentences(sentences):
                    topic, subtopic, tags = infer_topic(" ".join(sent_block), os.path.basename(path))
                    metadata = {
                        "source": os.path.basename(path),
                        "section": section_title,
                        "topic": topic,
                        "subtopic": subtopic,
                        "content_type": infer_content_type(" ".join(sent_block), source_kind),
                        "difficulty": infer_difficulty(path, source_kind),
                        "relevance_score": infer_relevance(source_kind),
                        "tags": tags or [topic],
                        "source_kind": source_kind,
                        "priority": 2 if source_kind == "agency" else 1,
                    }
                    text = build_chunk_text(section_title, sent_block, os.path.basename(path))
                    chunk_id = f"{slugify(os.path.basename(path))}-{uuid.uuid4().hex[:8]}"
                    chunks.append(Chunk(text=text, metadata=metadata, id=chunk_id))
            unique_chunks = dedupe_chunks(chunks)
            self._persist(unique_chunks)
            return len(unique_chunks)

        if ext in (".xlsx", ".csv"):
            text = self._load_table_text(path)
            sentences = sentence_split(text)
            chunks: List[Chunk] = []
            for sent_block in chunk_sentences(sentences):
                metadata = {
                    "source": os.path.basename(path),
                    "topic": "case_study",
                    "subtopic": None,
                    "content_type": "case_study",
                    "difficulty": "advanced",
                    "relevance_score": infer_relevance("case_study"),
                    "tags": [slugify(os.path.basename(path)), "case_study"],
                    "source_kind": "case_study",
                    "priority": 2,
                }
                text_block = build_chunk_text("Case Study", sent_block, os.path.basename(path))
                chunk_id = f"case-{slugify(os.path.basename(path))}-{uuid.uuid4().hex[:8]}"
                chunks.append(Chunk(text=text_block, metadata=metadata, id=chunk_id))
            unique_chunks = dedupe_chunks(chunks)
            self._persist(unique_chunks)
            return len(unique_chunks)

        raise ValueError(f"Unsupported file type: {ext}")

    def _load_table_text(self, path: str) -> str:
        if path.lower().endswith(".csv"):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f"Table: {os.path.basename(path)}\n" + f.read()
        try:
            import pandas as pd
        except ImportError as exc:
            raise RuntimeError("pandas is required to ingest Excel files; install pandas") from exc
        xls = pd.ExcelFile(path)
        sheets = []
        for sheet in xls.sheet_names:
            df = xls.parse(sheet).dropna(how="all")
            if df.empty:
                continue
            snippet = df.head(40).to_csv(index=False)
            sheets.append(f"Sheet: {sheet}\n{snippet}")
        return "\n\n".join(sheets)

    def _persist(self, chunks: List[Chunk], batch_size: int = 64) -> None:
        def normalize(meta: Dict[str, object]) -> Dict[str, object]:
            cleaned = {}
            for k, v in meta.items():
                if isinstance(v, list):
                    cleaned[k] = ",".join(str(x) for x in v)
                else:
                    cleaned[k] = v
            return cleaned

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            self.collection.upsert(
                ids=[c.id for c in batch],
                documents=[c.text for c in batch],
                metadatas=[normalize(c.metadata) for c in batch],
            )


# ---- CLI ------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Build or extend the RAG database.")
    parser.add_argument("--rebuild", action="store_true", help="Drop and rebuild full DB")
    parser.add_argument("--add", type=str, help="Add a single file without full rebuild")
    args = parser.parse_args()

    pipeline = RAGPipeline()

    if args.rebuild:
        count = pipeline.rebuild()
        print(f"Rebuilt collection with {count} chunks")
        return

    if args.add:
        count = pipeline.add_file(args.add)
        print(f"Added {count} chunks from {args.add}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
