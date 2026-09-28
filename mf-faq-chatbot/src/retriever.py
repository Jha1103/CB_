"""Retrieval module - keyword-based (no embedding API needed)."""
from typing import List, Dict, Any
import re


def retrieve(query: str) -> List[Dict[str, Any]]:
    """
    Retrieve relevant chunks using keyword matching.
    No embedding API needed - works offline.
    """
    from src.loader import load_structured_facts
    from src.chunker import chunk_scheme_facts
    from src.config import DATA_DIR

    facts = load_structured_facts(DATA_DIR)
    chunks = chunk_scheme_facts(facts)

    query_lower = query.lower()

    # Category keywords for matching
    category_keywords = {
        "expense_ratio": ["expense", "expense ratio", "ter", "total expense"],
        "exit_load": ["exit load", "exit", "redemption charge", "exit charge"],
        "min_sip": ["minimum sip", "min sip", "sip amount", "minimum investment sip", "sip"],
        "min_lumpsum": ["minimum lumpsum", "min lumpsum", "lumpsum amount", "minimum investment lumpsum", "lumpsum"],
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

    # Filter chunks by category
    if query_category:
        filtered = [c for c in chunks if c["category"] == query_category]
        if filtered:
            # Add score for compatibility
            for c in filtered:
                c["score"] = 0.9
            return filtered

    # Fallback: return all chunks with low score
    for c in chunks:
        c["score"] = 0.1
    return chunks[:5]
