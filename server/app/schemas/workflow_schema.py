from typing import List, Optional, Dict, Any, Union, Literal
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, validator

# --- Scheduling Schemas ---
class ScheduleConfig(BaseModel):
    time: str = Field(..., description="Time in HH:MM format (24h)", pattern=r"^\d{2}:\d{2}$")
    days: Optional[List[str]] = Field(default=None, description="List of days (mon, tue, etc.) for weekly")
    day_of_month: Optional[int] = Field(default=None, ge=1, le=31, description="Day of month (1-31)")
    month: Optional[int] = Field(default=None, ge=1, le=12, description="Month (1-12) for yearly")
    cron: Optional[str] = Field(default=None, description="Custom cron expression")

    @validator("days", pre=True)
    def validate_days(cls, v):
        if isinstance(v, str):
            return [d.strip().lower() for d in v.split(",")]
        return [d.lower() for d in v] if v else None

# --- Core Workflow Schemas ---
class WorkflowBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    workflow_type: str = "custom"

class WorkflowCreate(WorkflowBase):
    status: Optional[str] = "draft"
    
    # Trigger Configuration
    trigger_type: Literal["immediate", "scheduled"] = "immediate"
    frequency: Optional[Literal["once", "daily", "weekly", "monthly", "yearly"]] = "once"
    schedule_config: Optional[ScheduleConfig] = None
    
    is_active: bool = True

class WorkflowRead(WorkflowBase):
    id: UUID
    status: str
    
    trigger_type: str
    frequency: Optional[str] = None
    schedule_config: Optional[Dict[str, Any]] = None 
    
    start_node_id: Optional[UUID] = None
    end_node_ids: Optional[List[UUID]] = None

    is_active: bool

    created_at: datetime
    updated_at: datetime
    
    # Execution Stats
    last_run_at: Optional[datetime] = None
    total_runs: int = 0

    class Config:
        from_attributes = True

class WorkflowNodeSchema(BaseModel):
    id: UUID
    node_type: str
    tool: Optional[str] = None
    arguments: Optional[Dict[str, Any]] = None
    position_x: float = 0
    position_y: float = 0

    class Config:
        from_attributes = True

class WorkflowEdgeSchema(BaseModel):
    id: UUID
    source_node: UUID
    target_node: UUID
    condition: Optional[str] = None

    class Config:
        from_attributes = True

class WorkflowGraphUpdate(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]

class WorkflowExecutionRead(BaseModel):
    id: UUID
    workflow_id: UUID
    status: str
    execution_type: str = "immediate"
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    logs: Optional[Dict[str, Any]] = None
    celery_task_id: Optional[str] = None

    class Config:
        from_attributes = True

# --- Structured Output Schema (For Planner Agent) ---
class AIWorkflowNode(BaseModel):
    id: str
    node_type: Literal["tool", "condition", "delay", "approval"]
    tool: Optional[str] = None
    arguments: Dict[str, Any] = Field(default_factory=dict)
    position_x: float = 0
    position_y: float = 0

class AIWorkflowEdge(BaseModel):
    id: str
    source: str
    target: str
    condition: Optional[str] = None

class AIWorkflowGraph(BaseModel):
    workflow_name: str
    workflow_type: str
    trigger: Dict[str, Any]
    nodes: List[AIWorkflowNode]
    edges: List[AIWorkflowEdge]
    start_node_id: str
    end_node_ids: List[str]

