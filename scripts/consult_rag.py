import os
import chromadb
from typing import Optional

# Initialize ChromaDB
# Path relative to this file: ../backend/knowledge_base/chroma_db
# We are running from project root, so path is backend/knowledge_base/chroma_db
CHROMA_PATH = os.path.abspath("backend/knowledge_base/chroma_db")

if not os.path.exists(CHROMA_PATH):
    print(f"WARNING: ChromaDB path not found at {CHROMA_PATH}")
    # Try the path from server.py just in case
    CHROMA_PATH = os.path.abspath("mcp-servers/backend/knowledge_base/chroma_db")
    if not os.path.exists(CHROMA_PATH):
        print(f"WARNING: ChromaDB path also not found at {CHROMA_PATH}")

try:
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(name="agency_knowledge")
except Exception as e:
    print(f"Error initializing ChromaDB: {e}")
    exit(1)

def _rerank(results, boost_agency: bool = True):
    """Apply lightweight reranking using relevance_score/priority from metadata."""
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]
    scored = []
    for doc, meta, dist in zip(docs, metas, dists):
        score = dist
        priority = meta.get("priority", 1)
        relevance = meta.get("relevance_score", 0)
        if boost_agency and meta.get("source_kind") == "agency":
            score -= 0.2
        score -= 0.1 * (priority - 1)
        score -= 0.05 * relevance
        scored.append((score, doc, meta))
    scored.sort(key=lambda x: x[0])
    return scored

def query_knowledge(
    query: str,
    n_results: int = 10,
    content_type: Optional[str] = None,
    topic: Optional[str] = None,
    boost_agency: bool = True
) -> str:
    where_filter = {}
    if content_type:
        where_filter["content_type"] = content_type
    if topic:
        where_filter["topic"] = topic
    if not where_filter:
        where_filter = None

    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        reranked = _rerank(results, boost_agency=boost_agency)
        output = []
        for score, doc, metadata in reranked[:n_results]:
            source = metadata.get("source", "Unknown")
            doc_type = metadata.get("content_type", metadata.get("type", "Unknown"))
            topic_meta = metadata.get("topic", "")
            output.append(
                f"**[{doc_type}] {source}** (topic: {topic_meta}, score: {score:.3f})\n{doc}\n"
            )

        if not output:
            return "No relevant knowledge found."

        return "\n---\n".join(output)
    except Exception as e:
        return f"Error querying knowledge base: {str(e)}"

def get_methodology(task_type: str) -> str:
    task_queries = {
        "keyword_research": "keyword research methodology iterative approach match types seed keywords",
        "ad_copy": "RSA responsive search ads headlines descriptions sentence case best practices",
        "campaign_structure": "campaign naming convention ad group structure URL strategy",
        "audit": "account audit optimization recommendations quality score",
    }
    query = task_queries.get(task_type, task_type)
    return query_knowledge(query, n_results=5, content_type="methodology")

print("--- STRATEGY FOR CLEANING SERVICES ---")
print(query_knowledge("cleaning services keyword research denmark"))

print("\n--- CAMPAIGN STRUCTURE METHODOLOGY ---")
print(get_methodology("campaign_structure"))

print("\n--- AD COPY METHODOLOGY ---")
print(get_methodology("ad_copy"))
