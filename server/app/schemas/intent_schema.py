from pydantic import BaseModel, Field
from typing import Literal, Optional, List

class MainAgentIntent(BaseModel):
    intent: Literal["chat", "task", "clarify"] = Field(
        description="Whether the user wants to chat, needs a task, or if we need to clarify their request."
    )
    task_description: Optional[str] = Field(
        description="If intent is 'task', a clear, purified description of what the user wants to automate."
    )
    clarification_question: Optional[str] = Field(
        description="If the user's task request is missing critical information (like recipient, time, or specific action), provide a helpful question to ask the user."
    )
    is_task_robust: bool = Field(
        description="True if the task request contains all necessary parameters to be executed without further questions."
    )
    needs_memory: bool = Field(
        description="True if the query seems to refer to past preferences or personal facts."
    )
    search_query: Optional[str] = Field(
        description="Optimized search query for memory retrieval."
    )
