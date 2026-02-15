from datetime import datetime, timezone
from typing import Optional, Dict, Any
from uuid import uuid4, UUID

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from pgvector.sqlalchemy import Vector

class VectorMemory(SQLModel, table=True):
    __tablename__ = "vector_memory"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    content: str = Field(sa_column=Column(Text, nullable=False))
    
    # Vector column for embeddings (defaulting to 1536 for OpenAI)
    embedding: Any = Field(sa_column=Column(Vector(1536)))
    
    meta_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    # Relationship
    user: Optional["User"] = Relationship(back_populates="vector_memories")
