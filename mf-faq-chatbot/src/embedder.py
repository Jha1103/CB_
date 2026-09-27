"""Generate embeddings using sentence-transformers."""
from sentence_transformers import SentenceTransformer
from typing import List
from src.config import EMBEDDING_MODEL

_model = None


def get_model():
    """Lazy-load the embedding model."""
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed a list of texts into vectors."""
    model = get_model()
    return model.encode(texts, show_progress_bar=False).tolist()


def embed_query(query: str) -> List[float]:
    """Embed a single query."""
    return embed_texts([query])[0]
