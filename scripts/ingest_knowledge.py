"""
Compatibility wrapper around rag_pipeline.

Use this script to rebuild or incrementally add a file:
    python scripts/ingest_knowledge.py --rebuild
    python scripts/ingest_knowledge.py --add <path>
"""

import argparse
from rag_pipeline import RAGPipeline


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rebuild", action="store_true", help="Drop and rebuild the DB")
    parser.add_argument("--add", type=str, help="Add a single file to the DB")
    args = parser.parse_args()

    pipeline = RAGPipeline()
    if args.rebuild:
        count = pipeline.rebuild()
        print(f"Rebuilt with {count} chunks")
        return
    if args.add:
        count = pipeline.add_file(args.add)
        print(f"Added {count} chunks from {args.add}")
        return
    parser.print_help()


if __name__ == "__main__":
    main()
