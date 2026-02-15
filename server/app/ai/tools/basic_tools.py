from typing import Dict, Any
from uuid import UUID
from langchain_core.tools import tool

@tool
def summarize_text(text: str) -> Dict[str, Any]:
    """Summarize the given text."""
    return {
        "status": "success",
        "summary": f"Summary: {text[:200]}..."
    }

@tool
def current_user_id(user_id: UUID) -> Dict[str, Any]:
    """Return the current user id (debug / identity tool)."""
    return {
        "status": "success",
        "user_id": str(user_id)
    }
