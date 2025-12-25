from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.models.message import Message
from app.db.models.chat import Chat



# CREATE MESSAGE
async def create_message(session: AsyncSession, chat_id: UUID, sender: str, content: str) -> Message:

    message = Message(
        chat_id=chat_id,
        sender=sender,
        content=content,
        created_at=datetime.now(timezone.utc)
    )

    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message



# GET ALL MESSAGES BY CHAT
async def get_messages_by_chat( session: AsyncSession, chat_id: UUID ) -> List[Message]:

    query = (
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(Message.created_at.asc())
    )

    result = await session.execute(query)
    return result.scalars().all()



# GET SINGLE MESSAGE (BY ID)
async def get_message_by_id(session: AsyncSession, message_id: UUID) -> Optional[Message]:

    query = select(Message).where(Message.id == message_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()



# DELETE MESSAGE
async def delete_message(session: AsyncSession, message: Message):
    await session.delete(message)
    await session.commit()
