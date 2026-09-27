"""Conversation memory for MF FAQ Assistant."""
from collections import deque
from typing import Dict, List, Any
import threading

# In-memory conversation store: session_id -> deque of messages
_conversations: Dict[str, deque] = {}
_lock = threading.Lock()

MAX_HISTORY = 10


def get_history(session_id: str) -> List[Dict[str, str]]:
    """Get conversation history for a session."""
    with _lock:
        if session_id not in _conversations:
            return []
        return list(_conversations[session_id])


def add_message(session_id: str, role: str, content: str) -> None:
    """Add a message to the conversation history."""
    with _lock:
        if session_id not in _conversations:
            _conversations[session_id] = deque(maxlen=MAX_HISTORY)
        _conversations[session_id].append({"role": role, "content": content})


def clear_history(session_id: str) -> None:
    """Clear conversation history for a session."""
    with _lock:
        if session_id in _conversations:
            _conversations[session_id].clear()


def get_context_window(session_id: str, max_messages: int = MAX_HISTORY) -> str:
    """Get the conversation history as a formatted context string."""
    history = get_history(session_id)
    if not history:
        return ""

    # Take the last N messages
    recent = history[-max_messages:]

    context_parts = []
    for msg in recent:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            context_parts.append(f"User: {content}")
        elif role == "assistant":
            context_parts.append(f"Assistant: {content}")

    return "\n".join(context_parts)
