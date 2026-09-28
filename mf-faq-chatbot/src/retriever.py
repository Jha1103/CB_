"""Retrieval module for MF FAQ (cloud-based)."""
from typing import List, Dict, Any
from src.embedder import embed_query
from src.vector_store import search, initialize_store, is_initialized
from src.config import TOP_K, SCORE_THRESHOLD
import re


def retrieve(query: str) -> List[Dict[str, Any]]:
    """
    Retrieve relevant chunks for a query.
    Returns filtered and ranked chunks.
    """
    # Initialize store on first use
    if not is_initialized():
        from src.loader import load_structured_facts
        from src.chunker import chunk_scheme_facts
        from src.config import DATA_DIR
        facts = load_structured_facts(DATA_DIR)
        chunks = chunk_scheme_facts(facts)
        initialize_store(chunks)

    # Embed the query
    query_embedding = embed_query(query)

    # Search
    results = search(query_embedding, top_k=TOP_K)

    # Filter by score threshold
    filtered = [r for r in results if r["score"] >= SCORE_THRESHOLD]

    # Query-category matching
    query_lower = query.lower()
    category_keywords = {
        "expense_ratio": ["expense", "expense ratio", "ter", "total expense"],
        "exit_load": ["exit load", "exit", "redemption charge", "exit charge"],
        "min_sip": ["minimum sip", "min sip", "sip amount", "minimum investment sip"],
        "min_lumpsum": ["minimum lumpsum", "min lumpsum", "lumpsum amount", "minimum investment lumpsum"],
        "benchmark": ["benchmark", "index", "nifty", "bse", "sensex"],
        "risk_level": ["risk", "riskometer", "risk level", "very high", "moderate", "low risk"],
        "fund_manager": ["fund manager", "manager", "managed by", "who manages", "who is the fund manager", "fund manager of"],
        "aum": ["aum", "asset under management", "fund size", "corpus"],
        "nav": ["nav", "net asset value", "nav price"],
        "lock_in": ["lock in", "lock-in", "lock in period", "elss lock"],
        "tax": ["tax", "taxation", "ltcg", "stcg", "capital gains tax"],
        "stamp_duty": ["stamp duty", "stamp"],
        "launch_date": ["launch", "launched", "inception", "started"],
        "investment_objective": ["objective", "goal", "aim", "purpose", "investment objective"],
        "holdings": ["holdings", "top holdings", "portfolio", "stocks", "companies", "top 10"],
    }

    # Detect query category
    query_category = None
    for category, keywords in category_keywords.items():
        if any(kw in query_lower for kw in keywords):
            query_category = category
            break

    # If we detected a category, filter results to that category
    if query_category:
        category_results = [r for r in filtered if r["metadata"].get("category_type") == query_category]
        if category_results:
            return category_results

    return filtered
