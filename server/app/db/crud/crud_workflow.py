from uuid import UUID
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.models.workflow import Workflow

async def create_workflow(
    session: AsyncSession, 
    user_id: UUID, 
    name: str, 
    chat_id: Optional[UUID] = None,
    description: Optional[str] = None,
    workflow_type: str = "custom",
    trigger_type: str = "immediate",
    frequency: str = "once",
    schedule_config: Optional[Dict[str, Any]] = None,
    start_node_id: Optional[UUID] = None,
    end_node_ids: Optional[List[UUID]] = None
) -> Workflow:
    workflow = Workflow(
        user_id=user_id,
        chat_id=chat_id,
        name=name,
        description=description,
        workflow_type=workflow_type,
        trigger_type=trigger_type,
        frequency=frequency,
        schedule_config=schedule_config,
        start_node_id=start_node_id,
        end_node_ids=end_node_ids
    )
    session.add(workflow)
    await session.commit()
    await session.refresh(workflow)
    return workflow

async def get_workflow_by_id(session: AsyncSession, workflow_id: UUID) -> Optional[Workflow]:
    from sqlalchemy.orm import selectinload
    query = select(Workflow).where(Workflow.id == workflow_id).options(
        selectinload(Workflow.nodes),
        selectinload(Workflow.edges)
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def get_workflow_by_chat_id(session: AsyncSession, chat_id: UUID) -> Optional[Workflow]:
    from sqlalchemy.orm import selectinload
    query = select(Workflow).where(Workflow.chat_id == chat_id).options(
        selectinload(Workflow.nodes),
        selectinload(Workflow.edges)
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def get_user_workflows(session: AsyncSession, user_id: UUID) -> List[Workflow]:
    query = select(Workflow).where(Workflow.user_id == user_id).order_by(Workflow.updated_at.desc())
    result = await session.execute(query)
    return result.scalars().all()

async def update_workflow(
    session: AsyncSession, 
    workflow: Workflow, 
    **kwargs
) -> Workflow:
    for key, value in kwargs.items():
        if hasattr(workflow, key):
            setattr(workflow, key, value)
    
    workflow.updated_at = datetime.now(timezone.utc)
    session.add(workflow)
    await session.commit()
    await session.refresh(workflow)
    return workflow

async def delete_workflow(session: AsyncSession, workflow: Workflow):
    await session.delete(workflow)
    await session.commit()

async def get_all_active_scheduled_workflows(session: AsyncSession) -> List[Workflow]:
    query = select(Workflow).where(
        Workflow.trigger_type == "scheduled",
        Workflow.is_active == True
    )
    result = await session.execute(query)
    return result.scalars().all()
