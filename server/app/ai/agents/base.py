from typing import Any, Optional, Type, TypeVar
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from app.core.config import BaseSettings
import os

T = TypeVar("T", bound=BaseModel)

class BaseAgent:
    def __init__(
        self, 
        model_name: str = "gpt-4o", 
        temperature: float = 0,
        system_prompt: Optional[str] = None
    ):
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.system_prompt = system_prompt

    async def get_structured_output(
        self, 
        output_schema: Type[T], 
        user_input: str,
        chat_history: Optional[list[BaseMessage]] = None
    ) -> T:
        structured_llm = self.llm.with_structured_output(output_schema, method="function_calling")
        
        messages = []
        if self.system_prompt:
            messages.append(("system", self.system_prompt))
        
        if chat_history:
            messages.extend(chat_history)
            
        messages.append(("user", user_input))
        
        return await structured_llm.ainvoke(messages)
