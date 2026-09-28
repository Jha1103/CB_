"""Cloud-based embedding using Hugging Face Inference API (no local model)."""
import os
import requests
import numpy as np
from typing import List, Optional

# Hugging Face Inference API (free, no API key needed for basic usage)
HF_API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
HF_API_KEY = os.environ.get("HF_API_KEY", "")  # Optional: set for higher rate limits

# Cache for embeddings (avoid repeated API calls)
_embedding_cache = {}


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed texts using Hugging Face Inference API."""
    results = []
    for text in texts:
        if text in _embedding_cache:
            results.append(_embedding_cache[text])
            continue

        try:
            headers = {"Content-Type": "application/json"}
            if HF_API_KEY:
                headers["Authorization"] = f"Bearer {HF_API_KEY}"

            response = requests.post(
                HF_API_URL,
                headers=headers,
                json={"inputs": text},
                timeout=30,
            )
            response.raise_for_status()
            embedding = response.json()

            # Cache the result
            _embedding_cache[text] = embedding
            results.append(embedding)

        except Exception as e:
            print(f"Embedding API error: {e}")
            # Fallback: return zero vector
            results.append([0.0] * 384)

    return results


def embed_query(query: str) -> List[float]:
    """Embed a single query."""
    return embed_texts([query])[0]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    a_arr = np.array(a)
    b_arr = np.array(b)
    dot = np.dot(a_arr, b_arr)
    norm_a = np.linalg.norm(a_arr)
    norm_b = np.linalg.norm(b_arr)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))
