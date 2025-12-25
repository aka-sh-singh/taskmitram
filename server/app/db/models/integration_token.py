from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4, UUID
from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint


class IntegrationToken(SQLModel, table=True):
    __tablename__ = "integration_tokens"
    __table_args__ = (
    UniqueConstraint("user_id", "provider"),
    )


    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)

    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)

    provider: str = Field(nullable=False, max_length=50)

    access_token: str = Field(nullable=False)
    refresh_token: Optional[str] = Field(default=None)
    scopes: Optional[str] = Field(default=None)

    expires_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    user: Optional["User"] = Relationship(back_populates="integration_tokens")
