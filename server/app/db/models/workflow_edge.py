from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4, UUID

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID

class WorkflowEdge(SQLModel, table=True):
    __tablename__ = "workflow_edges"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    workflow_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("workflows.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    source_node: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("workflow_nodes.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    target_node: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("workflow_nodes.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    condition: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    # Relationships
    workflow: Optional["Workflow"] = Relationship(back_populates="edges")
