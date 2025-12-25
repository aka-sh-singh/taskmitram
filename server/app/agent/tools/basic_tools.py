from uuid import UUID
from langchain_core.tools import tool

@tool
def summarize_text(text: str) -> str:
    """Summarize the given text."""
    return f"Summary: {text[:200]}..."

@tool
def current_user_id(user_id: UUID) -> str:
    """Return the current user id (debug / identity tool)."""
    return f"Current user id is {user_id}"
