from uuid import UUID
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.models.workflow_execution import WorkflowExecution

async def create_execution(
    session: AsyncSession,
    workflow_id: UUID,
    user_id: UUID,
    execution_type: str = "manual"
) -> WorkflowExecution:
    execution = WorkflowExecution(
        workflow_id=workflow_id,
        user_id=user_id,
        status="pending",
        execution_type=execution_type
    )
    session.add(execution)
    await session.commit()
    await session.refresh(execution)
    return execution

async def update_execution_status(
    session: AsyncSession,
    execution: WorkflowExecution,
    status: str,
    logs: Optional[Dict[str, Any]] = None
) -> WorkflowExecution:
    execution.status = status
    if logs:
        execution.logs = logs
    
    if status == "running" and not execution.started_at:
        execution.started_at = datetime.now(timezone.utc)
    elif status in ["completed", "failed"]:
        execution.finished_at = datetime.now(timezone.utc)
        
    session.add(execution)
    await session.commit()
    await session.refresh(execution)
    return execution
