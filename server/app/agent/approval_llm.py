from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2,
)

SYSTEM_PROMPT = """
You generate approval requests for dangerous actions.

Rules:
- Describe EXACTLY the provided action.
- Do NOT add or remove information.
- Do NOT change intent.
- Ask clearly for Yes/No approval.
- Be concise and clear.
"""

async def generate_approval_message(payload: dict) -> str:
    """
    payload is deterministic and trusted.
    LLM is only used for phrasing.
    """

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=str(payload)),
    ]

    resp = await llm.ainvoke(messages)
    return resp.content.strip()
