from typing import Optional, List, Literal, Dict, Any
from pydantic import BaseModel, Field


class TriggerConfig(BaseModel):
    type: Literal["immediate", "scheduled"]
    frequency: Literal[
        "once", "daily", "weekly", "monthly", "yearly"
    ]
    date: Optional[str] = None
    time: Optional[str] = None
    days: Optional[List[Literal[
        "mon", "tue", "wed", "thu", "fri", "sat", "sun"
    ]]] = None
    day_of_month: Optional[int] = None
    month: Optional[int] = None
    timezone: str = "Asia/Kolkata"




class WorkflowNode(BaseModel):
    id: str = Field(
        description="Unique node ID. Must be UUID string."
    )

    node_type: Literal[
        "tool",
        "condition",
        "delay",
        "approval"
    ]

    tool: Optional[Literal[
        "send_gmail",
        "list_drive_files",
        "read_drive_file_content",
        "create_drive_file",
        "list_github_repositories",
        "list_github_issues",
        "create_github_issue",
        "read_github_file_content",
        "read_spreadsheet_values",
        "update_spreadsheet_values",
        "append_spreadsheet_values",
        "create_spreadsheet"
    ]] = None

    arguments: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments for tool execution"
    )

    position_x: float = Field(
        default=0,
        description="React Flow X coordinate"
    )

    position_y: float = Field(
        default=0,
        description="React Flow Y coordinate"
    )




class WorkflowEdge(BaseModel):
    id: str = Field(
        description="Unique edge ID"
    )

    source: str = Field(
        description="Source node ID"
    )

    target: str = Field(
        description="Target node ID"
    )

    condition: Optional[str] = Field(
        default=None,
        description="Optional condition label"
    )




class WorkflowGraphStructuredOutput(BaseModel):
    workflow_name: str
    workflow_type: Literal[
        "email",
        "drive",
        "github",
        "sheets",
    ]
    trigger: TriggerConfig
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
    start_node_id: str
    end_node_ids: List[str]
