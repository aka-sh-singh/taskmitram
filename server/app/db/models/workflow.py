from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from uuid import uuid4, UUID

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB

class Workflow(SQLModel, table=True):
    __tablename__ = "workflows"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    chat_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("chats.id", ondelete="CASCADE"),
            nullable=True,
            unique=True,
            index=True,
        )
    )
    name: str = Field(nullable=False, max_length=200)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    status: str = Field(default="draft", max_length=20)
    workflow_type: str = Field(default="custom", max_length=50) # email | drive | github | sheets | custom
    
    # Automation / Scheduling
    trigger_type: str = Field(default="immediate", max_length=20)  # immediate | scheduled
    frequency: Optional[str] = Field(default="once", max_length=50) # once | daily | weekly | monthly | yearly
    schedule_config: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB)) 
    
    # Execution Flow
    start_node_id: Optional[UUID] = Field(default=None, sa_column=Column(PGUUID(as_uuid=True), nullable=True))
    end_node_ids: Optional[List[UUID]] = Field(default=None, sa_column=Column(JSONB)) # List of terminal node UUIDs

    is_active: bool = Field(default=True)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    # Relationships
    user: Optional["User"] = Relationship(back_populates="workflows")
    nodes: List["WorkflowNode"] = Relationship(
        back_populates="workflow",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "passive_deletes": True},
    )
    edges: List["WorkflowEdge"] = Relationship(
        back_populates="workflow",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "passive_deletes": True},
    )
    executions: List["WorkflowExecution"] = Relationship(
        back_populates="workflow",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "passive_deletes": True},
    )

    # Execution Metadata
    last_run_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    total_runs: int = Field(default=0)
