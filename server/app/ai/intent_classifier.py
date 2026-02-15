from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.0,  # Strictness is key
)

# Define Structured Output Schema
class ApprovalDecision(BaseModel):
    decision: str = Field(
        ..., 
        description="The decision made by the user. Must be one of: 'approved', 'rejected', 'ambiguous'."
    )
    reasoning: str = Field(
        ..., 
        description="Brief explanation of why this decision was determined."
    )

# Structured LLM
structured_llm = llm.with_structured_output(ApprovalDecision, method="function_calling")

SYSTEM_PROMPT = """
You are a strict decision classifier.
Your job is to determine if the user has APPROVED or REJECTED a pending action based on their response.

Rules:
1. If the user clearly agrees (e.g., "yes", "sure", "go ahead", "send it", "looks good"), correct decision is 'approved'.
2. If the user clearly disagrees (e.g., "no", "cancel", "don't send", "stop"), correct decision is 'rejected'.
3. If the user asks a question, changes the subject, or is unclear, correct decision is 'ambiguous'.

Output must be strictly one of: 'approved', 'rejected', 'ambiguous'.
"""

async def classify_approval_intent(user_input: str) -> str:
    """
    Uses LLM to classify user intent as 'approved', 'rejected', or 'ambiguous'.
    """
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_input),
    ]

    try:
        result = await structured_llm.ainvoke(messages)
        return result.decision
    except Exception as e:
        # Fallback to ambiguous if LLM fails
        return "ambiguous"
