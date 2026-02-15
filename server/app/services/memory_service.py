import os
from uuid import UUID
from typing import List, Optional, Dict, Any

from sqlmodel.ext.asyncio.session import AsyncSession
from openai import AsyncOpenAI

from app.db.crud import crud_memory
from app.db.models.memory import VectorMemory


class MemoryService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "text-embedding-3-small" # or text-embedding-ada-002

    async def _get_embedding(self, text: str) -> List[float]:
        response = await self.client.embeddings.create(
            input=[text.replace("\n", " ")],
            model=self.model
        )
        return response.data[0].embedding

    async def add_memory(
        self,
        session: AsyncSession,
        user_id: UUID,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> VectorMemory:
        embedding = await self._get_embedding(content)
        return await crud_memory.create_memory_entry(
            session, user_id, content, embedding, metadata
        )

    async def search_memory(
        self,
        session: AsyncSession,
        user_id: UUID,
        query: str,
        limit: int = 5
    ) -> List[VectorMemory]:
        query_embedding = await self._get_embedding(query)
        return await crud_memory.search_memory(
            session, user_id, query_embedding, limit
        )

    async def clear_user_memory(self, session: AsyncSession, user_id: UUID):
        await crud_memory.delete_all_user_memory(session, user_id)
