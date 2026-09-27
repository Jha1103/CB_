#!/usr/bin/env python3
"""Build the vector store index from structured facts."""
import os
import sys

# Set environment variable to use CPU only
os.environ["TORCH_DEVICE"] = "cpu"

from src.loader import load_structured_facts
from src.chunker import chunk_scheme_facts
from src.vector_store import add_chunks, clear_collection, count_chunks
from src.config import DATA_DIR


def main():
    print("Loading structured facts...")
    facts = load_structured_facts(DATA_DIR)
    print(f"  Loaded {len(facts['schemes'])} schemes")

    print("Generating chunks...")
    chunks = chunk_scheme_facts(facts)
    print(f"  Generated {len(chunks)} chunks")

    print("Clearing existing collection...")
    clear_collection()

    print("Embedding and storing chunks...")
    add_chunks(chunks)
    print(f"  Stored {count_chunks()} chunks in ChromaDB")

    print("Build complete!")


if __name__ == "__main__":
    main()
