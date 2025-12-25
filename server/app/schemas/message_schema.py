from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field



# CREATE MESSAGE
class MessageCreate(BaseModel):
    sender: str = Field(..., pattern="^(user|agent)$")
    content: str = Field(..., min_length=1)



# MESSAGE RESPONSE
class MessageRead(BaseModel):
    id: UUID
    chat_id: UUID
    sender: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
