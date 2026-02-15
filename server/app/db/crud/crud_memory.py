from uuid import UUID
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from sqlmodel import select, delete
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text

from app.db.models.memory import VectorMemory


async def create_memory_entry(
    session: AsyncSession,
    user_id: UUID,
    content: str,
    embedding: List[float],
    metadata: Optional[Dict[str, Any]] = None
) -> VectorMemory:
    memory = VectorMemory(
        user_id=user_id,
        content=content,
        embedding=embedding,
        meta_data=metadata
    )
    session.add(memory)
    await session.commit()
    await session.refresh(memory)
    return memory


async def get_memory_by_id(session: AsyncSession, memory_id: UUID) -> Optional[VectorMemory]:
    query = select(VectorMemory).where(VectorMemory.id == memory_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def search_memory(
    session: AsyncSession,
    user_id: UUID,
    query_embedding: List[float],
    limit: int = 5
) -> List[VectorMemory]:
    """
    Perform semantic search using pgvector's cosine distance (<=>).
    """
    # SQLModel/SQLAlchemy pgvector search
    query = (
        select(VectorMemory)
        .where(VectorMemory.user_id == user_id)
        .order_by(VectorMemory.embedding.cosine_distance(query_embedding))
        .limit(limit)
    )
    result = await session.execute(query)
    return result.scalars().all()


async def delete_memory_entry(session: AsyncSession, memory: VectorMemory):
    await session.delete(memory)
    await session.commit()


async def delete_all_user_memory(session: AsyncSession, user_id: UUID):
    query = delete(VectorMemory).where(VectorMemory.user_id == user_id)
    await session.execute(query)
    await session.commit()
