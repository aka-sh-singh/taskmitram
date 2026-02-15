from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.services import workflow_service
from app.ai.agents.executor_agent import ExecutorAgent
from typing import Optional
from uuid import UUID
import asyncio

@celery_app.task(name="execute_workflow_task")
def execute_workflow_task(workflow_id: str, user_id: str, execution_id: Optional[str] = None):
    """
    Celery task to run a workflow execution in the background.
    """
    async def run():
        async with SessionLocal() as session:
            # 1. Fetch Workflow
            workflow = await workflow_service.get_workflow(session, UUID(workflow_id))
            if not workflow:
                print(f"Workflow {workflow_id} not found")
                return

            # 2. Handle Execution Record
            if not execution_id:
                from app.db.models.workflow_execution import WorkflowExecution
                execution = WorkflowExecution(
                    workflow_id=UUID(workflow_id),
                    user_id=UUID(user_id),
                    status="pending",
                    execution_type="scheduled" if workflow.trigger_type == "scheduled" else "manual"
                )
                session.add(execution)
                await session.commit()
                await session.refresh(execution)
                exec_id = execution.id
            else:
                exec_id = UUID(execution_id)

            # 3. Initialize ExecutorAgent
            executor = ExecutorAgent(session, exec_id)

            # 3. Execute
            await executor.execute(workflow, UUID(user_id))

    # Run the async function in the Celery worker's event loop
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # This shouldn't happen in a standard Celery worker, but good for safety
        asyncio.ensure_future(run())
    else:
        loop.run_until_complete(run())

@celery_app.task(name="resume_workflow_task")
def resume_workflow_task(workflow_id: str, execution_id: str, user_id: str, node_id: str):
    """
    Resumes a paused workflow execution from a specific node after approval.
    """
    async def run():
        async with SessionLocal() as session:
            workflow = await workflow_service.get_workflow(session, UUID(workflow_id))
            if not workflow: return

            executor = ExecutorAgent(session, UUID(execution_id))
            # Resume execution specifically from the approved node
            await executor.execute(workflow, UUID(user_id), resume_node_id=UUID(node_id))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())

@celery_app.task(name="scheduler_heartbeat")
def scheduler_heartbeat():
    """
    Heartbeat task to check for scheduled workflows that need to run.
    """
    async def run():
        async with SessionLocal() as session:
            try:
                # Check for active scheduled workflows
                workflows = await workflow_service.list_active_scheduled_workflows(session)
                from datetime import datetime, timezone
                for wf in workflows:
                    if workflow_service.is_workflow_due(wf):
                        print(f"Triggering scheduled workflow: {wf.name} ({wf.id})")
                        
                        # 1. Update last_run_at immediately to prevent duplicate runs
                        wf.last_run_at = datetime.now(timezone.utc)
                        session.add(wf)
                        await session.commit()

                        # 2. Trigger the execution task
                        execute_workflow_task.delay(
                            str(wf.id), 
                            str(wf.user_id)
                        )
            except Exception as e:
                # Handle missing tables gracefully (e.g. if backend hasn't run init_db yet)
                if "relation" in str(e) and "does not exist" in str(e):
                    print("Waiting for database tables to be created by the backend...")
                else:
                    print(f"Error in scheduler heartbeat: {e}")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
