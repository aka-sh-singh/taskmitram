from datetime import datetime, timezone
from typing import Optional, Dict, Any
from uuid import uuid4, UUID

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB

class WorkflowNode(SQLModel, table=True):
    __tablename__ = "workflow_nodes"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    workflow_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("workflows.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    node_type: str = Field(nullable=False, max_length=50) # tool | condition | delay | approval
    tool: Optional[str] = Field(default=None, max_length=100) # send_gmail, list_drive_files, etc.
    arguments: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB)) # Tool arguments
    
    # React Flow Positioning
    position_x: float = Field(default=0.0)
    position_y: float = Field(default=0.0)
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    # Relationships
    workflow: Optional["Workflow"] = Relationship(back_populates="nodes")
