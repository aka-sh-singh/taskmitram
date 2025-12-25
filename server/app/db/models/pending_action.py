from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.dialects.postgresql import JSONB


class PendingAction(SQLModel, table=True):
    __tablename__ = "pending_actions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    chat_id: UUID = Field(
        sa_column=Column(PGUUID(as_uuid=True), nullable=False, index=True)
    )

    user_id: UUID = Field(
        sa_column=Column(PGUUID(as_uuid=True), nullable=False, index=True)
    )

    tool_name: str = Field(nullable=False, max_length=100)

    tool_args: dict = Field(
        sa_column=Column(JSONB, nullable=False)
    )

    status: str = Field(
        default="awaiting_approval", max_length=30
    )  # awaiting_approval | approved | rejected

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    expires_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
