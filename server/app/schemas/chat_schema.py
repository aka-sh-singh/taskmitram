from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field

from app.schemas.message_schema import MessageRead



# CREATE CHAT
class ChatCreate(BaseModel):
    title: str = Field(default="New Chat", max_length=200)



# UPDATE CHAT TITLE
class ChatUpdate(BaseModel):
    title: str = Field(..., max_length=200)



# CHAT RESPONSE (BASIC)
class ChatRead(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    last_activity: datetime
    chat_uuid: UUID

    class Config:
        from_attributes = True



# CHAT WITH MESSAGES (DETAILED)
class ChatReadWithMessages(ChatRead):
    messages: List[MessageRead] = []
