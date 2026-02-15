from uuid import UUID
from typing import List, Optional, Dict, Any
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.crud import crud_workflow, crud_workflow_node, crud_workflow_edge
from app.db.models.workflow import Workflow

async def create_new_workflow(
    session: AsyncSession, 
    user_id: UUID, 
    name: str, 
    description: Optional[str] = None
) -> Workflow:
    return await crud_workflow.create_workflow(
        session=session,
        user_id=user_id,
        name=name,
        description=description
    )

async def list_user_workflows(session: AsyncSession, user_id: UUID) -> List[Workflow]:
    return await crud_workflow.get_user_workflows(session, user_id)

async def get_workflow(session: AsyncSession, workflow_id: UUID) -> Optional[Workflow]:
    return await crud_workflow.get_workflow_by_id(session, workflow_id)

async def update_workflow_details(
    session: AsyncSession, 
    workflow_id: UUID, 
    **kwargs
) -> Optional[Workflow]:
    workflow = await crud_workflow.get_workflow_by_id(session, workflow_id)
    if not workflow:
        return None
    return await crud_workflow.update_workflow(session, workflow, **kwargs)

async def delete_workflow(session: AsyncSession, workflow_id: UUID) -> bool:
    workflow = await crud_workflow.get_workflow_by_id(session, workflow_id)
    if not workflow:
        return False
    await crud_workflow.delete_workflow(session, workflow)
    return True

async def save_workflow_graph(
    session: AsyncSession,
    workflow_id: UUID,
    nodes_data: List[Dict[str, Any]],
    edges_data: List[Dict[str, Any]]
) -> bool:
    try:
        workflow = await crud_workflow.get_workflow_by_id(session, workflow_id)
        if not workflow:
            return False

        # Delete existing
        from app.db.models.workflow_node import WorkflowNode
        from app.db.models.workflow_edge import WorkflowEdge
        from sqlmodel import delete

        await session.execute(delete(WorkflowEdge).where(WorkflowEdge.workflow_id == workflow_id))
        await session.execute(delete(WorkflowNode).where(WorkflowNode.workflow_id == workflow_id))
        
        # 2. Add new nodes
        node_map = {}
        for n in nodes_data:
            import uuid
            node_id = uuid.UUID(n['id']) if isinstance(n['id'], str) and len(n['id']) == 36 else uuid.uuid4()
            
            db_node = await crud_workflow_node.create_workflow_node(
                session=session,
                workflow_id=workflow_id,
                node_type=n.get('node_type') or n.get('type', 'tool'),
                tool=n.get('tool') or n.get('data', {}).get('tool'),
                arguments=n.get('arguments') or n.get('data', {}).get('arguments') or {},
                position_x=n.get('position_x') or n.get('position', {}).get('x', 0),
                position_y=n.get('position_y') or n.get('position', {}).get('y', 0),
                id=node_id
            )
            node_map[n['id']] = db_node.id
        
        # 3. Add new edges
        for e in edges_data:
            await crud_workflow_edge.create_workflow_edge(
                session=session,
                workflow_id=workflow_id,
                source_node=node_map[e['source']],
                target_node=node_map[e['target']],
                condition=e.get('condition') or e.get('label')
            )
        
        await session.commit()
        return True
    except Exception as e:
        print(f"Error saving workflow graph: {e}")
        await session.rollback()
        return False

async def execute_workflow(session: AsyncSession, workflow_id: UUID, user_id: UUID):
    from app.db.models.workflow_execution import WorkflowExecution
    execution = WorkflowExecution(
        workflow_id=workflow_id,
        user_id=user_id,
        status="pending",
        execution_type="manual"
    )
    session.add(execution)
    await session.commit()
    await session.refresh(execution)
    
    # Trigger Celery Task
    from app.core.celery_app import celery_app
    celery_app.send_task("execute_workflow_task", args=[str(workflow_id), str(user_id), str(execution.id)])
    
    return execution

async def list_active_scheduled_workflows(session: AsyncSession) -> List[Workflow]:
    return await crud_workflow.get_all_active_scheduled_workflows(session)

async def get_workflow_by_chat_id(session: AsyncSession, chat_id: UUID) -> Optional[Workflow]:
    return await crud_workflow.get_workflow_by_chat_id(session, chat_id)

async def orchestrate_ai_workflow(
    session: AsyncSession,
    user_id: UUID,
    chat_id: UUID,
    plan: Any # WorkflowGraphStructuredOutput
) -> Workflow:
    """
    Orchestrates the creation/replacement of a workflow based on an AI plan.
    Handles the 1:1 chat-workflow mapping and node/edge linkage.
    """
    import uuid
    from app.db.models.pending_action import PendingAction

    # 1. Maintain 1:1 Mapping - Delete existing workflow for this chat
    existing_wf = await crud_workflow.get_workflow_by_chat_id(session, chat_id)
    if existing_wf:
        await crud_workflow.delete_workflow(session, existing_wf)

    # 2. Create New Workflow
    new_workflow = await crud_workflow.create_workflow(
        session=session,
        user_id=user_id,
        chat_id=chat_id,
        name=plan.workflow_name,
        workflow_type=plan.workflow_type,
        trigger_type=plan.trigger.type,
        frequency=plan.trigger.frequency,
        schedule_config=plan.trigger.model_dump()
    )

    # 3. Create Nodes
    node_map = {}
    for ai_node in plan.nodes:
        # Try to use the AI suggested ID if it's a valid UUID, otherwise generate a fresh one
        try:
            node_id = uuid.UUID(ai_node.id)
        except (ValueError, TypeError, AttributeError):
            node_id = uuid.uuid4()

        db_node = await crud_workflow_node.create_workflow_node(
            session=session,
            workflow_id=new_workflow.id,
            node_type=ai_node.node_type,
            tool=ai_node.tool,
            arguments=ai_node.arguments,
            position_x=ai_node.position_x,
            position_y=ai_node.position_y,
            id=node_id
        )
        node_map[ai_node.id] = db_node.id

    # 4. Create Edges
    for ai_edge in plan.edges:
        if ai_edge.source in node_map and ai_edge.target in node_map:
            await crud_workflow_edge.create_workflow_edge(
                session=session,
                workflow_id=new_workflow.id,
                source_node=node_map[ai_edge.source],
                target_node=node_map[ai_edge.target],
                condition=ai_edge.condition
            )

    # 5. Connect start/end nodes & Handle scheduling
    updates = {
        "start_node_id": node_map.get(plan.start_node_id),
        "end_node_ids": [str(node_map[eid]) for eid in plan.end_node_ids if eid in node_map]
    }

    if plan.trigger.type == "scheduled":
        updates["is_active"] = False # Pause until approved
        # Create HITL action
        hitl = PendingAction(
            workflow_id=new_workflow.id,
            user_id=user_id,
            tool_name="automation_approval",
            tool_args={"schedule": plan.trigger.model_dump()},
            status="awaiting_approval"
        )
        session.add(hitl)
    
    await crud_workflow.update_workflow(session, new_workflow, **updates)
    
    return new_workflow

def is_workflow_due(workflow: Workflow) -> bool:
    """
    Checks if a scheduled workflow is due for execution.
    Handles different frequencies: once, daily, weekly, monthly, yearly.
    """
    from datetime import datetime
    import pytz

    if not workflow.is_active or workflow.trigger_type != "scheduled":
        return False

    config = workflow.schedule_config or {}
    tz_name = config.get("timezone", "Asia/Kolkata")
    try:
        tz = pytz.timezone(tz_name)
    except:
        tz = pytz.timezone("Asia/Kolkata")

    now = datetime.now(tz)
    
    # Check if run today already (for recurring tasks)
    if workflow.last_run_at:
        last_run = workflow.last_run_at.astimezone(tz)
        if last_run.date() == now.date() and workflow.frequency != "once":
            # Already ran today, don't run again (for daily/weekly)
            return False

    # 1. Check Time
    scheduled_time_str = config.get("time") # HH:MM
    if not scheduled_time_str:
        return False
    
    sch_hour, sch_min = map(int, scheduled_time_str.split(":"))
    
    # We allow a small window (e.g. within 5 minutes of scheduled time)
    # but since heartbeat is every 10s, we check if we are in the correct minute
    if now.hour != sch_hour or now.minute != sch_min:
        return False

    # 2. Check Date/Day Frequency
    freq = workflow.frequency
    
    if freq == "once":
        scheduled_date_str = config.get("date") # YYYY-MM-DD
        if not scheduled_date_str: return False
        if now.strftime("%Y-%m-%d") != scheduled_date_str:
            return False
        # If once and already ran (at any time in the past), don't run
        if workflow.last_run_at:
            return False

    elif freq == "weekly":
        scheduled_days = config.get("days", []) # ["mon", "tue", ...]
        current_day = now.strftime("%a").lower()
        if current_day not in scheduled_days:
            return False

    elif freq == "monthly":
        scheduled_day_of_month = config.get("day_of_month")
        if now.day != scheduled_day_of_month:
            return False

    elif freq == "yearly":
        scheduled_month = config.get("month")
        scheduled_day_of_month = config.get("day_of_month")
        if now.month != scheduled_month or now.day != scheduled_day_of_month:
            return False

    # Daily has no additional checks beyond time and "not yet run today"
    return True
