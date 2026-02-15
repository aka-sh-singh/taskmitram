from app.ai.agents.base import BaseAgent
from app.schemas.memory_schema import MemorySaveDecision

MEMORY_SYSTEM_PROMPT = """You are the Memory Management Agent for Taskमित्र.

Your job is to analyze the user's latest message and decide if it contains informative, personal, or task-relevant information that should be remembered for future context.

Guidelines:
1. "Save" information like: user preferences, recurring tasks, project details, contact info, specific goals, or factual statements about their workflow.
2. "DON'T save" information like: greetings (hi, hello), small talk, vague questions, or temporary status checks.
3. Be concise when extracting the information.

You must return a structured output with a 'should_save' boolean, the 'extracted_information', and a 'category'.
"""

class MemoryAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            model_name="gpt-4o-mini", # Mini is enough for this classification task
            temperature=0,
            system_prompt=MEMORY_SYSTEM_PROMPT
        )

    async def analyze_memory(self, user_input: str) -> MemorySaveDecision:
        return await self.get_structured_output(
            output_schema=MemorySaveDecision,
            user_input=user_input
        )
