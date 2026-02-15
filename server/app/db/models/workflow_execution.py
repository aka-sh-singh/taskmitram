from datetime import datetime, timezone
from typing import Optional, Dict, Any
from uuid import uuid4, UUID

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB

class WorkflowExecution(SQLModel, table=True):
    __tablename__ = "workflow_executions"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    workflow_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("workflows.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    user_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    execution_type: str = Field(default="manual", max_length=20)  # manual | scheduled
    status: str = Field(default="pending", max_length=20)  # pending | running | completed | failed
    started_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    finished_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    logs: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    celery_task_id: Optional[str] = Field(default=None, max_length=100)
    
    current_node_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PGUUID(as_uuid=True), nullable=True)
    )
    
    context: Optional[Dict[str, Any]] = Field(
        default=None, 
        sa_column=Column(JSONB)
    )

    # Relationships
    workflow: Optional["Workflow"] = Relationship(back_populates="executions")
