from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

from app.db.crud.crud_chat import get_chat_by_id, update_last_activity
from app.db.crud.crud_message import create_message, get_messages_by_chat
from app.schemas.message_schema import MessageCreate
from app.db.models.user import User


# SEND A MESSAGE (USER → CHAT)
async def send_user_message_service(session: AsyncSession, user: User, chat_id: UUID, data: MessageCreate):

    chat = await get_chat_by_id(session, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    if chat.user_id != user.id:
        raise HTTPException(status_code=403, detail="This is not your chat")

    
    message = await create_message(session, chat_id, "user", data.content)

    
    await update_last_activity(session, chat)

    return message


# SEND AGENT MESSAGE (AI → CHAT)
async def send_agent_message_service(session: AsyncSession, chat_id: UUID, content: str):
    message = await create_message(session, chat_id, "agent", content)
    return message


# GET ALL MESSAGES FOR A CHAT
async def get_chat_messages_service(session: AsyncSession, user: User, chat_id: UUID):


    chat = await get_chat_by_id(session, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    
    if chat.user_id != user.id:
        raise HTTPException(status_code=403, detail="You cannot access this chat")

    messages = await get_messages_by_chat(session, chat_id)
    return messages
