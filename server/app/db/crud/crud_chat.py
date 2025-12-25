from uuid import UUID
from typing import List, Optional
from datetime import datetime, timezone

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.models.chat import Chat



# CREATE CHAT
async def create_chat(session: AsyncSession, user_id: UUID, title: str) -> Chat:
    chat = Chat(
        user_id=user_id,
        title=title,
        last_activity=datetime.now(timezone.utc),
    )

    session.add(chat)
    await session.commit()
    await session.refresh(chat)
    return chat



# GET ALL CHATS FOR A USER
async def get_user_chats(session: AsyncSession, user_id: UUID) -> List[Chat]:
    query = select(Chat).where(Chat.user_id == user_id).order_by(Chat.last_activity.desc())
    result = await session.execute(query)
    return result.scalars().all()



# GET SINGLE CHAT (BY ID)
async def get_chat_by_id(session: AsyncSession, chat_id: UUID) -> Optional[Chat]:
    query = select(Chat).where(Chat.id == chat_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()



# GET CHAT BY chat_uuid (safe for frontend sharing)
async def get_chat_by_uuid(session: AsyncSession, chat_uuid: UUID) -> Optional[Chat]:
    query = select(Chat).where(Chat.chat_uuid == chat_uuid)
    result = await session.execute(query)
    return result.scalar_one_or_none()



# UPDATE CHAT TITLE
async def update_chat_title(session: AsyncSession, chat: Chat, new_title: str) -> Chat:
    chat.title = new_title
    chat.last_activity = datetime.now(timezone.utc)

    session.add(chat)
    await session.commit()
    await session.refresh(chat)
    return chat



# UPDATE CHAT LAST ACTIVITY (when a new message comes)
async def update_last_activity(session: AsyncSession, chat: Chat):
    chat.last_activity = datetime.now(timezone.utc)
    session.add(chat)
    await session.commit()



# DELETE CHAT
async def delete_chat(session: AsyncSession, chat: Chat):
    await session.delete(chat)
    await session.commit()

# DELETE ALL CHATS FOR A USER
async def delete_all_user_chats(session: AsyncSession, user_id: UUID):
    from sqlmodel import delete
    query = delete(Chat).where(Chat.user_id == user_id)
    await session.execute(query)
    await session.commit()
