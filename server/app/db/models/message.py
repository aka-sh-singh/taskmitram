# app/db/models/message.py
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4, UUID

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.dialects.postgresql import JSONB


class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)

    chat_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("chats.id", ondelete="CASCADE"),
            nullable=False,
        )
    )

    sender: str = Field(nullable=False, max_length=10)  # e.g. 'user'|'agent'|'system'
    content: str = Field(nullable=False)

    # optional structured metadata (tool calls, usage, tokens, etc.)
    msg_metadata: Optional[dict] = Field(default=None, sa_column=Column("msg_metadata", JSONB, nullable=True))

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    chat: Optional["Chat"] = Relationship(back_populates="messages")