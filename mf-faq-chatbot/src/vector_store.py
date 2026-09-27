"""ChromaDB vector store operations."""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from src.config import CHROMA_COLLECTION, CHROMA_PERSIST_DIR

_client = None
_collection = None


def get_client():
    """Get or create ChromaDB client."""
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    return _client


def get_collection():
    """Get or create the collection (lazy-loaded)."""
    global _collection
    if _collection is None:
        client = get_client()
        _collection = client.get_or_create_collection(
            name=CHROMA_COLLECTION,
            metadata={"hnsw:space": "cosine"}
        )
    return _collection


def add_chunks(chunks: List[Dict[str, Any]]):
    """Add chunks to the vector store."""
    collection = get_collection()

    ids = [c["id"] for c in chunks]
    texts = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    # Embed texts
    from src.embedder import embed_texts
    embeddings = embed_texts(texts)

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )


def search(query_embedding: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
    """Search for similar chunks."""
    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    chunks = []
    if results["ids"] and results["ids"][0]:
        for i, chunk_id in enumerate(results["ids"][0]):
            chunks.append({
                "id": chunk_id,
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
                "score": 1 - results["distances"][0][i],  # cosine similarity
            })
    return chunks


def count_chunks() -> int:
    """Get the number of chunks in the store."""
    collection = get_collection()
    return collection.count()


def clear_collection():
    """Delete and recreate the collection."""
    global _collection
    client = get_client()
    try:
        client.delete_collection(CHROMA_COLLECTION)
    except Exception:
        pass
    _collection = None
