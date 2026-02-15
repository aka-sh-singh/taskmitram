from uuid import UUID, uuid4
from typing import List, Optional, Dict, Any
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.models.workflow_node import WorkflowNode

async def create_workflow_node(
    session: AsyncSession,
    workflow_id: UUID,
    node_type: str,
    tool: Optional[str] = None,
    arguments: Optional[Dict[str, Any]] = None,
    position_x: float = 0.0,
    position_y: float = 0.0,
    id: Optional[UUID] = None
) -> WorkflowNode:
    node = WorkflowNode(
        id=id or uuid4(),
        workflow_id=workflow_id,
        node_type=node_type,
        tool=tool,
        arguments=arguments,
        position_x=position_x,
        position_y=position_y
    )
    session.add(node)
    await session.commit()
    await session.refresh(node)
    return node

async def get_workflow_nodes(session: AsyncSession, workflow_id: UUID) -> List[WorkflowNode]:
    query = select(WorkflowNode).where(WorkflowNode.workflow_id == workflow_id)
    result = await session.execute(query)
    return result.scalars().all()
