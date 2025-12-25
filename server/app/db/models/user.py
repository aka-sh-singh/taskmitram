from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4, UUID

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    username: str = Field(nullable=False, unique=True, max_length=50)
    email: str = Field(nullable=False, unique=True, max_length=100)
    hashed_password: str = Field(nullable=False)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


    chats: List["Chat"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "passive_deletes": True},
    )

    refresh_tokens: List["RefreshToken"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "passive_deletes": True},
    )

    integration_tokens: List["IntegrationToken"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "passive_deletes": True},
    )
