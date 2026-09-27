#!/usr/bin/env python3
"""Test the RAG retrieval pipeline interactively."""
import sys
from src.classifier import classify_query
from src.retriever import retrieve
from src.generator import generate_answer
from src.embedder import embed_query
from src.vector_store import search
from src.config import TOP_K, SCORE_THRESHOLD


def test_retrieval(query: str):
    """Test retrieval for a single query."""
    print("=" * 80)
    print(f"QUERY: \"{query}\"")
    print("=" * 80)

    # Step 1: Classify
    classification = classify_query(query)
    print(f"\n[1] CLASSIFICATION")
    print(f"    Type: {classification['type']}")
    print(f"    Confidence: {classification['confidence']}")

    if classification["type"] != "factual":
        result = generate_answer(classification["type"], [], query)
        print(f"\n[2] NON-FACTUAL — skipping retrieval")
        print(f"    Answer: {result['answer'][:100]}...")
        return

    # Step 2: Embed query
    print(f"\n[2] EMBEDDING")
    query_embedding = embed_query(query)
    print(f"    Dimensions: {len(query_embedding)}")
    print(f"    First 5 dims: {[round(x, 4) for x in query_embedding[:5]]}")

    # Step 3: Search ChromaDB
    print(f"\n[3] CHROMADB SEARCH (top_k={TOP_K}, threshold={SCORE_THRESHOLD})")
    results = search(query_embedding, top_k=TOP_K)

    if not results:
        print("    No results found!")
        return

    for i, r in enumerate(results):
        marker = " <-- SELECTED" if i == 0 else ""
        print(f"\n    Result {i+1} (score: {r['score']:.4f}){marker}")
        print(f"    ID: {r['id']}")
        print(f"    Text: {r['text'][:80]}...")
        print(f"    Source: {r['metadata'].get('source_url', 'N/A')[:60]}")

    # Step 4: Filter by threshold
    filtered = [r for r in results if r["score"] >= SCORE_THRESHOLD]
    print(f"\n[4] FILTERING")
    print(f"    Results above threshold ({SCORE_THRESHOLD}): {len(filtered)}/{len(results)}")

    # Step 5: Generate answer
    print(f"\n[5] ANSWER GENERATION")
    result = generate_answer(classification["type"], filtered, query)
    print(f"    Type: {result['type']}")
    print(f"    Answer: {result['answer']}")
    print(f"    Source: {result.get('source', 'N/A')}")
    print(f"    Confidence: {result.get('confidence', 'N/A')}")
    print()


def main():
    if len(sys.argv) > 1:
        # Test single query from command line
        query = " ".join(sys.argv[1:])
        test_retrieval(query)
    else:
        # Interactive mode
        print("RAG Retrieval Tester")
        print("Enter a query to test retrieval (or 'quit' to exit)")
        print()

        while True:
            try:
                query = input("Query> ").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if not query or query.lower() in ("quit", "exit", "q"):
                break

            test_retrieval(query)
            print()


if __name__ == "__main__":
    main()
