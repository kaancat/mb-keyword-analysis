import os
import chromadb
from typing import Optional

from mcp.server.fastmcp import FastMCP

# Initialize MCP Server
mcp = FastMCP(
    "Google Ads RAG Knowledge",
    instructions="""
    This server provides access to Monday Brew's Google Ads methodology,
    case studies, and best practices. Use these tools to:
    - Query for relevant knowledge before starting tasks
    - Get specific methodology for keyword research, ad copy, etc.
    - Access example analyses from previous clients
    - Get strict deliverable schemas for output
    """,
)

# Initialize ChromaDB
# Path relative to this file: ../../backend/knowledge_base/chroma_db
CHROMA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../knowledge_base/chroma_db")
)

# Ensure the path exists to avoid errors, though it should exist if DB is built
if not os.path.exists(CHROMA_PATH):
    print(f"WARNING: ChromaDB path not found at {CHROMA_PATH}")

client = chromadb.PersistentClient(path=CHROMA_PATH)
# Use default embedding function (all-MiniLM-L6-v2)
collection = client.get_collection(name="agency_knowledge")


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


@mcp.tool()
def query_knowledge(
    query: str,
    n_results: int = 10,
    filter_type: Optional[str] = None,
    topic: Optional[str] = None,
    content_type: Optional[str] = None,
    boost_agency: bool = True,
) -> str:
    """
    Semantic search over the Google Ads knowledge base with metadata-aware ranking.

    Args:
        query: Natural language query (e.g., "match type rules for phrase match")
        n_results: Number of results to return (default 10)
        filter_type: Deprecated alias; use content_type.
        topic: Optional topic filter (e.g., "keyword_match_types")
        content_type: Optional filter - "case_study", "methodology", "example", "warning", "best_practice"
        boost_agency: Prioritize agency-authored content when True.
    """
    where_filter = {}
    if filter_type:
        where_filter["content_type"] = filter_type
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


@mcp.tool()
def get_methodology(task_type: str) -> str:
    """
    Get methodology for a specific task type.

    Args:
        task_type: One of "keyword_research", "ad_copy", "campaign_structure", "audit"

    Returns:
        Relevant methodology and best practices
    """
    task_queries = {
        "keyword_research": "keyword research methodology iterative approach match types seed keywords",
        "ad_copy": "RSA responsive search ads headlines descriptions sentence case best practices",
        "campaign_structure": "campaign naming convention ad group structure URL strategy",
        "audit": "account audit optimization recommendations quality score",
    }

    query = task_queries.get(task_type, task_type)
    return query_knowledge(query, n_results=15, content_type="methodology")


@mcp.tool()
def list_examples() -> str:
    """
    List all available example analyses from previous clients.

    Returns:
        List of client examples with descriptions
    """
    examples = {
        "spacefinder": "Norwegian office rental - 308 keywords, 21 ad groups, location-based",
        "karim_design": "Danish wedding dresses - misspelling handling, booking intent",
        "companyons": "Copenhagen co-working - location × service matrix",
        "helenes_horeklinik": "Hearing clinic - medical services, city-specific",
        "haus20": "Office hotel - German/Danish bilingual",
    }

    output = "# Available Example Analyses\n\n"
    for name, desc in examples.items():
        output += f"- **{name}**: {desc}\n"
    output += "\nUse `get_example(client_name)` to get details."

    return output


@mcp.tool()
def get_example(client_name: str) -> str:
    """
    Get detailed analysis for a specific client example.

    Args:
        client_name: Client name (e.g., "spacefinder", "karim_design")

    Returns:
        Case study details including campaign structure, keywords, ad copy patterns
    """
    return query_knowledge(
        f"{client_name} campaign structure keywords ad groups",
        n_results=10,
        content_type="case_study",
    )


@mcp.tool()
def get_deliverable_schema(schema_type: str) -> str:
    """
    Get the official Monday Brew schema for a deliverable tab.

    Args:
        schema_type: "keyword_analysis", "campaign_structure", "ad_copy", "roi_calculator", or "all"

    Returns:
        JSON Schema and a Golden Example.
    """
    valid_types = [
        "keyword_analysis",
        "campaign_structure",
        "ad_copy",
        "roi_calculator",
    ]

    if schema_type == "all":
        output = "# Monday Brew Deliverable Schemas\n\n"
        for st in valid_types:
            try:
                schema_path = os.path.join(
                    os.path.dirname(__file__), "../../schemas", f"{st}.schema.json"
                )
                with open(schema_path, "r") as f:
                    output += f"## {st}\n{f.read()}\n\n"
            except Exception as e:
                output += f"Error reading {st}: {str(e)}\n"
        return output

    if schema_type not in valid_types:
        return f"Invalid schema type. Choose from: {', '.join(valid_types)} or 'all'"

    # Read schema file
    try:
        schema_path = os.path.join(
            os.path.dirname(__file__), "../../schemas", f"{schema_type}.schema.json"
        )
        with open(schema_path, "r") as f:
            schema_content = f.read()

        # Add helpful context for roi_calculator
        if schema_type == "roi_calculator":
            return f"""SCHEMA ({schema_type}):
{schema_content}

ROI CALCULATOR QUICK REFERENCE:
- Required inputs: budget (DKK), aov (DKK)
- Optional with defaults: profit_margin (0.30), close_rate (0.15), cpc (8), website_conv_rate (0.03)
- Use IF() formulas in Google Sheets to apply defaults when cells are empty
- Color coding: Yellow = input cells, Green = profitable, Red = unprofitable
"""

        return f"SCHEMA ({schema_type}):\n{schema_content}\n\nUse this schema to validate your output."
    except Exception as e:
        return f"Error reading schema: {str(e)}"


@mcp.resource("rag://stats")
def get_stats() -> str:
    """Get statistics about the knowledge base."""
    count = collection.count()
    return f"Knowledge base contains {count} embedded documents"


if __name__ == "__main__":
    mcp.run()
