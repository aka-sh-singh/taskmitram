from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import asyncio
import json

from app.agent.deep_agent import run_deep_agent





from app.db.session import get_session
from app.core.deps import get_current_user
from app.db.models.user import User

from app.schemas.chat_schema import (
    ChatCreate,
    ChatRead,
    ChatReadWithMessages,
    ChatUpdate
)

from app.schemas.message_schema import (
    MessageCreate,
    MessageRead
)

from app.services.chat_service import (
    create_chat_service,
    get_chats_service,
    get_chat_with_messages_service,
    update_chat_title_service,
    delete_chat_service,
    delete_all_chats_service,
)

from app.services.message_service import (
    send_user_message_service,
    send_agent_message_service,
    get_chat_messages_service,
)

from app.utils.title_gen import generate_title

router = APIRouter(prefix="/chats", tags=["Chats"])


#CREATE CHAT
@router.post("/", response_model=ChatRead)
async def create_chat(
    data: ChatCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await create_chat_service(session, current_user, data)


#GET ALL CHATS
@router.get("/", response_model=list[ChatRead])
async def get_chats(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await get_chats_service(session, current_user)


#GET SINGLE CHAT + MESSAGES
@router.get("/{chat_id}", response_model=ChatReadWithMessages)
async def get_chat_with_messages(
    chat_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await get_chat_with_messages_service(session, current_user, chat_id)


# UPDATE CHAT TITLE
@router.patch("/{chat_id}", response_model=ChatRead)
async def update_chat_title(
    chat_id: UUID,
    data: ChatUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await update_chat_title_service(session, current_user, chat_id, data)



# DELETE SINGLE CHAT
@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await delete_chat_service(session, current_user, chat_id)
    return {"message": "Chat deleted successfully"}


# DELETE ALL CHATS
@router.delete("/")
async def delete_all_chats(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await delete_all_chats_service(session, current_user)
    return {"message": "All chats deleted successfully"}






@router.post("/{chat_id}/messages")
async def send_user_message_stream(
    chat_id: str,
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    accept: str = Header(None),
):

    # A) Lazy chat creation
    if chat_id == "new":
        title = generate_title(data.content)
        new_chat = await create_chat_service(
            session,
            current_user,
            ChatCreate(title=title.strip())
        )
        chat_id = new_chat.id
        messages = []
    else:
        try:
            chat_uuid = UUID(chat_id)
        except:
            raise HTTPException(400, "Invalid chat id")

        chat_obj = await get_chat_with_messages_service(
            session,
            current_user,
            chat_uuid
        )
        if not chat_obj:
            raise HTTPException(404, "Chat does not exist. Start a new chat.")

        chat_id = chat_obj.id
        messages = chat_obj.messages


    # Save user message
    await send_user_message_service(session, current_user, chat_id, data)

    async def event_generator():
        accumulated_text = ""
        
        async for chunk in run_deep_agent(
            chat_id=chat_id,
            user_input=data.content,
            chat_messages=messages,
            user_id=current_user.id,
            session=session,
        ):
            accumulated_text += chunk
            yield chunk

        # Save agent message only after stream completes
        if accumulated_text:
            await send_agent_message_service(
                session,
                chat_id,
                accumulated_text.strip()
            )

    return StreamingResponse(
        event_generator(), 
        media_type="text/plain",
        headers={"X-Chat-Id": str(chat_id)}
    )



#GET ONLY MESSAGES
@router.get("/{chat_id}/messages", response_model=list[MessageRead])
async def get_chat_messages(
    chat_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await get_chat_messages_service(session, current_user, chat_id)
