#!/usr/bin/env python3
"""
Standalone script to query the ChromaDB codebase.
Run this after uploading a folder to test RAG retrieval.

Usage:
    python query_db.py "How is authentication implemented?"
    python query_db.py "What does the login function do?" --results 10
"""

import sys

from repositories.chroma_repository import chroma_repository


def format_results(results: dict) -> str:
    output = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if not documents:
        return "No results found. Make sure you've uploaded a codebase first."

    for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances), 1):
        similarity = 1 - dist
        output.append(f"\n{'=' * 60}")
        output.append(f"Result {i} | Similarity: {similarity:.2%}")
        output.append(f"{'=' * 60}")
        output.append(f"File: {meta.get('file_path', 'unknown')}")
        output.append(
            f"Type: {meta.get('chunk_type', 'unknown')} | Name: {meta.get('name', 'unknown')}"
        )
        if meta.get("parent_class"):
            output.append(f"Class: {meta.get('parent_class')}")
        output.append(
            f"Lines: {meta.get('start_line', '?')} - {meta.get('end_line', '?')}"
        )
        output.append(f"\n{doc}")

    return "\n".join(output)


def main():
    query = input("Enter query: ")

    try:
        stats = chroma_repository.get_stats()

        if stats.total_documents == 0:
            print("❌ No documents in database. Upload a codebase first using the API.")
            sys.exit(1)

        print(
            f"📁 Database: {stats.total_documents} chunks in '{stats.collection_name}'\n"
        )

        results = chroma_repository.query(query)
        formatted = format_results(results)
        print(formatted)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # main()
    data = chroma_repository.get_all()
    print(data)
