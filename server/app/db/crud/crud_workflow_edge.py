from uuid import UUID
from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.models.workflow_edge import WorkflowEdge

async def create_workflow_edge(
    session: AsyncSession,
    workflow_id: UUID,
    source_node: UUID,
    target_node: UUID,
    condition: Optional[str] = None
) -> WorkflowEdge:
    edge = WorkflowEdge(
        workflow_id=workflow_id,
        source_node=source_node,
        target_node=target_node,
        condition=condition
    )
    session.add(edge)
    await session.commit()
    await session.refresh(edge)
    return edge

async def get_workflow_edges(session: AsyncSession, workflow_id: UUID) -> List[WorkflowEdge]:
    query = select(WorkflowEdge).where(WorkflowEdge.workflow_id == workflow_id)
    result = await session.execute(query)
    return result.scalars().all()
