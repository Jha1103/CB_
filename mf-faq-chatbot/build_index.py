#!/usr/bin/env python3
"""Pre-download embedding model and cache embeddings (cloud-based)."""
import os

os.environ.setdefault("TORCH_DEVICE", "cpu")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

from src.loader import load_structured_facts
from src.chunker import chunk_scheme_facts
from src.vector_store import initialize_store, count_chunks
from src.config import DATA_DIR


def main():
    print("Loading structured facts...")
    facts = load_structured_facts(DATA_DIR)
    print(f"  Loaded {len(facts['schemes'])} schemes")

    print("Generating chunks...")
    chunks = chunk_scheme_facts(facts)
    print(f"  Generated {len(chunks)} chunks")

    print("Initializing in-memory store (downloads embeddings via API)...")
    initialize_store(chunks)
    print(f"  Stored {count_chunks()} chunks")

    print("Build complete!")


if __name__ == "__main__":
    main()
