"""
Add a single file to the RAG database without a full rebuild.

Usage:
    python scripts/add_to_rag.py /path/to/file.txt
"""

import argparse
import os
from rag_pipeline import RAGPipeline


def main():
    parser = argparse.ArgumentParser(description="Add one file to the RAG DB")
    parser.add_argument("path", help="File to ingest")
    args = parser.parse_args()

    if not os.path.exists(args.path):
        raise SystemExit(f"File not found: {args.path}")

    pipeline = RAGPipeline()
    count = pipeline.add_file(args.path)
    print(f"Ingested {count} chunks from {args.path}")


if __name__ == "__main__":
    main()
