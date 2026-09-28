"""LLM integration for MF FAQ Assistant using Groq."""
import os
from typing import List, Dict, Any, Optional

# Try to import openai
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Load .env file
from pathlib import Path
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

# Configuration
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "qwen/qwen3.8-27b")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

SYSTEM_PROMPT = """You are the MF FAQ Assistant. You answer factual questions about HDFC mutual fund schemes.

Rules:
- Only provide factual information from the given context
- Do NOT give investment advice or recommendations
- Do NOT compute or compare returns
- Keep answers concise (2-3 sentences)
- If the context doesn't contain the answer, say "I don't have that information in my corpus"
- Do NOT include "Source:" in your answer - it will be added automatically
- Be polite and professional

Available schemes: HDFC Large Cap, HDFC Flexi Cap, HDFC ELSS Tax Saver, HDFC Small Cap, HDFC Balanced Advantage

Facts-only. No investment advice."""


def is_llm_available() -> bool:
    """Check if LLM is configured and available."""
    return OPENAI_AVAILABLE and bool(GROQ_API_KEY) and GROQ_API_KEY != "gsk_your_api_key_here"


def generate_llm_answer(query: str, chunks: List[Dict[str, Any]], query_type: str = "factual", conversation_history: str = "") -> Optional[Dict[str, Any]]:
    """
    Generate an answer using Groq LLM with retrieved chunks as context.
    Returns None if LLM is not available.
    """
    if not is_llm_available():
        return None

    # Handle non-factual queries
    if query_type == "advice":
        return {
            "type": "refusal",
            "answer": (
                "I can only provide factual information about mutual fund schemes — "
                "I can't give investment advice or recommendations. "
                "For guidance on whether a scheme fits your goals, please consult a "
                "certified financial planner. You can learn more about mutual fund "
                "basics here: https://www.amfiindia.com"
            ),
            "source": "https://www.amfiindia.com",
            "scheme": None,
            "confidence": 1.0,
        }

    if query_type == "performance":
        link = chunks[0].get("source_url", "https://www.hdfcfund.com") if chunks else "https://www.hdfcfund.com"
        return {
            "type": "performance",
            "answer": (
                "I can't compute or compare returns. Please refer to the official "
                "factsheet for performance data: https://www.hdfcfund.com"
            ),
            "source": link,
            "scheme": None,
            "confidence": 1.0,
        }

    if query_type == "greeting":
        return {
            "type": "greeting",
            "answer": (
                "Hello! I'm the MF FAQ Assistant. I can answer factual questions "
                "about HDFC mutual fund schemes — expense ratio, exit load, "
                "minimum SIP, benchmark, risk level, and more. "
                "Facts-only. No investment advice."
            ),
            "source": None,
            "scheme": None,
            "confidence": 1.0,
        }

    if query_type in ("sentiment_positive", "sentiment_negative"):
        if query_type == "sentiment_positive":
            answer = (
                "Thank you for sharing that! I'm glad to hear the good news. "
                "However, I can only help with factual questions about HDFC mutual fund schemes. "
                "For example, you can ask me about expense ratio, exit load, minimum SIP, "
                "benchmark, risk level, fund manager, or lock-in period."
            )
        else:
            answer = (
                "I'm sorry to hear that. I hope things get better for you. "
                "However, I can only help with factual questions about HDFC mutual fund schemes. "
                "For example, you can ask me about expense ratio, exit load, minimum SIP, "
                "benchmark, risk level, fund manager, or lock-in period."
            )
        return {
            "type": "sentiment",
            "answer": answer,
            "source": None,
            "scheme": None,
            "confidence": 1.0,
        }

    # Build context from chunks
    context_parts = []
    for chunk in chunks[:5]:
        text = chunk.get("text", "")
        source = chunk.get("source_url", "")
        context_parts.append(f"- {text} (Source: {source})")

    context = "\n".join(context_parts) if context_parts else "No relevant context found."

    # Build messages with conversation history
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    # Add conversation history if available
    if conversation_history:
        messages.append({"role": "system", "content": f"Conversation history:\n{conversation_history}"})

    messages.append({"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"})

    try:
        client = OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            max_tokens=300,
            temperature=0.1,
        )

        answer_text = response.choices[0].message.content.strip()

        # Extract source from chunks if available
        source_url = chunks[0].get("source_url", "") if chunks else ""
        scheme_name = chunks[0].get("scheme_name", "") if chunks else ""

        return {
            "type": "factual",
            "answer": answer_text,
            "source": source_url,
            "scheme": scheme_name,
            "confidence": 0.9,
        }

    except Exception as e:
        print(f"LLM error: {e}")
        return None
