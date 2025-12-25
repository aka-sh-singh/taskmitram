from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

from app.db.crud.crud_chat import (
    create_chat,
    delete_chat,
    get_user_chats,
    get_chat_by_id,
    update_chat_title,
    delete_all_user_chats,
)
from app.db.crud.crud_message import get_messages_by_chat
from app.schemas.chat_schema import ChatCreate, ChatUpdate, ChatReadWithMessages
from app.db.models.user import User


# CREATE NEW CHAT FOR USER
async def create_chat_service(session: AsyncSession, user: User, data: ChatCreate):
    chat = await create_chat(session, user.id, data.title)
    return chat


# GET ALL CHATS FOR USER
async def get_chats_service(session: AsyncSession, user: User):
    chats = await get_user_chats(session, user.id)
    return chats


# GET SINGLE CHAT + ITS MESSAGES
async def get_chat_with_messages_service(session: AsyncSession, user: User, chat_id: UUID):

    chat = await get_chat_by_id(session, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")


    if chat.user_id != user.id:
        raise HTTPException(status_code=403, detail="This is not your chat")

    messages = await get_messages_by_chat(session, chat_id)

    return ChatReadWithMessages(
        id=chat.id,
        title=chat.title,
        created_at=chat.created_at,
        last_activity=chat.last_activity,
        chat_uuid=chat.chat_uuid,
        messages=messages,
    )


# UPDATE CHAT TITLE
async def update_chat_title_service(session: AsyncSession, user: User, chat_id: UUID, data: ChatUpdate):

    chat = await get_chat_by_id(session, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    if chat.user_id != user.id:
        raise HTTPException(status_code=403, detail="This is not your chat")

    updated_chat = await update_chat_title(session, chat, data.title)
    return updated_chat


# DELETE CHAT
async def delete_chat_service(session: AsyncSession, user: User, chat_id: UUID):
    
    chat = await get_chat_by_id(session, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    if chat.user_id != user.id:
        raise HTTPException(status_code=403, detail="This is not your chat")

    await delete_chat(session, chat)

# DELETE ALL CHATS
async def delete_all_chats_service(session: AsyncSession, user: User):
    await delete_all_user_chats(session, user.id)
    
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4

from sqlmodel.ext.asyncio.session import AsyncSession

# Use the new DeepAgent runner
from app.agent.deep_agent import run_deep_agent
from app.services.message_service import send_user_message_service, send_agent_message_service, get_chat_messages_service


async def process_message_with_agent(
    session: AsyncSession,
    current_user,
    chat_obj,
    message_create,  # expected to be same shape as MessageCreate schema
) -> Dict[str, Any]:
    """
    Persist the user message, run the deep agent on the thread.
    The agent handles HITL internally via PendingAction and returns a response string.
    """
    # 1) Persist the user message
    await send_user_message_service(session, current_user, chat_obj.id, message_create)

    # 2) Build message history
    msgs = await get_chat_messages_service(session, current_user, chat_obj.id)
    
    # 3) Invoke the agent
    # run_deep_agent expects the *full* list of DB messages, or handled internally if passed.
    # checking signature: async def run_deep_agent(*, chat_id, user_input, chat_messages, user_id, session) -> str
    
    # We pass the list of DB messages (msgs) so the agent can build history.
    # The user_input is the *new* message content (message_create.content). 
    # NOTE: `msgs` includes the user message we just saved (step 1).
    # `run_deep_agent` usually treats `user_input` as the "new" thing and appends it. 
    # If `msgs` already has it, we might duplicate it if not careful.
    # `run_deep_agent` implementation:
    #   history = to_langchain_messages(chat_messages)
    #   messages = [System] + history + [HumanMessage(user_input)]
    # So yes, it appends `user_input`. 
    # If we pass `msgs` (which includes the new msg), we might duplicate.
    # Let's pass `msgs[:-1]` (history without latest) OR 
    # just rely on `msgs` and pass `user_input=None`? No, `user_input` is str.
    
    # Best approach: Pass `msgs` EXCLUDING the one we just saved, 
    # OR let `run_deep_agent` handle it?
    # Actually `run_deep_agent` takes `user_input` string.
    # If we saved it, `msgs` has it.
    # Let's filter out the very last message from `msgs` if it matches our new input, 
    # OR simpler: just pass `msgs` that are *already* in DB before this new one? 
    # But we just saved it.
    
    # Let's pass `msgs` excluding the last one.
    history_msgs = msgs[:-1] if msgs else []

    try:
        agent_response_text = await run_deep_agent(
            chat_id=chat_obj.id,
            user_input=message_create.content,
            chat_messages=history_msgs,
            user_id=current_user.id,
            session=session
        )
    except Exception as e:
        return {"status": "error", "error": f"Agent invocation failed: {e}"}

    # 4) Persist the Agent Response
    agent_msg_row = await send_agent_message_service(session, chat_obj.id, agent_response_text)

    return {
        "status": "ok",
        "message": {
            "id": str(agent_msg_row.id),
            "role": "agent",
            "content": agent_msg_row.content,
            "created_at": agent_msg_row.created_at.isoformat(),
        },
    }