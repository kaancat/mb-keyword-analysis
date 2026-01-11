"""
Entry point to rebuild the RAG database using the unified rag_pipeline.

Run:
    python scripts/build_rag_db.py --rebuild
"""

from rag_pipeline import RAGPipeline


def main():
    pipeline = RAGPipeline()
    count = pipeline.rebuild()
    print(f"RAG Database rebuilt with {count} chunks")


if __name__ == "__main__":
    main()
