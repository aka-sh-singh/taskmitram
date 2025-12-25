from datetime import datetime, timezone
from typing import Optional, List
from uuid import uuid4, UUID

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID


class Chat(SQLModel, table=True):
    __tablename__ = "chats"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)

    user_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        )
    )

    title: str = Field(default="New Chat", max_length=200)
    chat_uuid: UUID = Field(default_factory=uuid4, unique=True, index=True)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    last_activity: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    user: Optional["User"] = Relationship(back_populates="chats")

    messages: List["Message"] = Relationship(
        back_populates="chat",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "passive_deletes": True},
    )
