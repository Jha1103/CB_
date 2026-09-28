"""In-memory vector store using numpy (no ChromaDB, minimal memory)."""
import numpy as np
from typing import List, Dict, Any, Optional
from src.embedder import embed_texts, cosine_similarity

# In-memory storage
_chunks: List[Dict[str, Any]] = []
_embeddings: List[List[float]] = []
_initialized = False


def initialize_store(chunks: List[Dict[str, Any]]):
    """Initialize the in-memory store with chunks."""
    global _chunks, _embeddings, _initialized

    if _initialized:
        return

    _chunks = chunks
    texts = [c["text"] for c in chunks]
    _embeddings = embed_texts(texts)
    _initialized = True
    print(f"Initialized in-memory store with {len(chunks)} chunks")


def search(query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
    """Search for similar chunks using cosine similarity."""
    if not _initialized:
        return []

    # Compute similarities
    similarities = []
    for i, emb in enumerate(_embeddings):
        sim = cosine_similarity(query_embedding, emb)
        similarities.append((i, sim))

    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)

    # Return top-k results
    results = []
    for i, sim in similarities[:top_k]:
        chunk = _chunks[i].copy()
        chunk["score"] = sim
        results.append(chunk)

    return results


def count_chunks() -> int:
    """Get the number of chunks in the store."""
    return len(_chunks)


def is_initialized() -> bool:
    """Check if the store is initialized."""
    return _initialized


def get_all_chunks() -> List[Dict[str, Any]]:
    """Get all chunks (for initialization)."""
    return _chunks
