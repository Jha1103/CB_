"""End-to-end RAG pipeline (cloud-based, minimal memory)."""
from typing import Dict, Any, Optional
from src.classifier import classify_query
from src.generator import generate_answer
from src.llm import generate_llm_answer, is_llm_available
from src.memory import get_context_window


def process_query(query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Process a user query through the full RAG pipeline:
    Classify -> Retrieve -> Generate (LLM if available, else template)
    """
    # Step 1: Classify
    classification = classify_query(query)
    query_type = classification["type"]

    # Step 2: Retrieve (only for factual queries)
    chunks = []
    if query_type == "factual":
        from src.retriever import retrieve
        chunks = retrieve(query)

    # Step 3: Get conversation history
    conversation_history = ""
    if session_id:
        conversation_history = get_context_window(session_id)

    # Step 4: Generate with LLM if available, else template
    result = None
    if is_llm_available():
        result = generate_llm_answer(query, chunks, query_type, conversation_history)

    # Fallback to template-based generation
    if result is None:
        result = generate_answer(query_type, chunks, query)

    # Step 5: Store in conversation history
    if session_id:
        from src.memory import add_message
        add_message(session_id, "user", query)
        add_message(session_id, "assistant", result.get("answer", ""))

    # Add classification info
    result["query_type"] = query_type
    result["retrieved_chunks"] = len(chunks)
    result["llm_used"] = is_llm_available()

    return result
