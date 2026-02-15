from typing import Any, Dict, List, Optional
from uuid import UUID
from app.db.models.workflow import Workflow
from app.db.models.workflow_node import WorkflowNode
from app.db.models.workflow_edge import WorkflowEdge
from app.db.models.workflow_execution import WorkflowExecution
from app.ai.tools import get_tool_by_name, is_approval_required
from app.db.crud.crud_workflow_execution import update_execution_status
from sqlmodel.ext.asyncio.session import AsyncSession
import asyncio

class ExecutorAgent:
    def __init__(self, session: AsyncSession, execution_id: UUID):
        self.session = session
        self.execution_id = execution_id
        self.context = {} # Shared state between nodes

    async def execute(self, workflow: Workflow, user_id: UUID, resume_node_id: Optional[UUID] = None):
        execution = await self.session.get(WorkflowExecution, self.execution_id)
        if not execution:
            return

        self.execution_type = getattr(execution, 'execution_type', 'manual')
        self.context = getattr(execution, 'context', {}) or {}
        
        await update_execution_status(self.session, execution, "running")
        
        try:
            # 1. Determine where to start
            current_node_id = resume_node_id or execution.current_node_id or workflow.start_node_id
            
            if not current_node_id:
                raise Exception("Start node not defined for workflow")

            # Flag to skip approval check ONLY for the very first node if we are resuming
            skip_approval = resume_node_id is not None

            while current_node_id:
                # Update current node in DB
                execution.current_node_id = current_node_id
                execution.context = self.context
                self.session.add(execution)
                await self.session.commit()

                # Get node
                node = next((n for n in workflow.nodes if n.id == current_node_id), None)
                if not node:
                    raise Exception(f"Node {current_node_id} not found")

                # Execute Node
                node_result = await self._execute_node(node, user_id, workflow.id, skip_approval=skip_approval)
                
                # Reset skip flag after first iteration
                skip_approval = False

                # Find next node (Branching support)
                edges = [e for e in workflow.edges if e.source_node == current_node_id]
                if not edges:
                    current_node_id = None
                elif len(edges) == 1:
                    current_node_id = edges[0].target_node
                else:
                    # Multiple edges: Evaluate conditions
                    next_node_id = None
                    for edge in edges:
                        if self._evaluate_condition(edge.condition, node_result):
                            next_node_id = edge.target_node
                            break
                    current_node_id = next_node_id

            # Final Cleanup
            execution.current_node_id = None # Clear after success
            await update_execution_status(self.session, execution, "completed", logs={"context": self.context})

        except Exception as e:
            # If it was a pause, don't log as a 'failed' failure if possible, 
            # but currently Executor uses Exception to stop the loop.
            if "PAUSED" in str(e):
                print(f"Workflow paused: {e}")
                return # Status already updated to 'paused' inside _run_tool
            
            print(f"Workflow execution failed: {e}")
            await update_execution_status(self.session, execution, "failed", logs={"error": str(e), "context": self.context})

    async def _execute_node(self, node: WorkflowNode, user_id: UUID, workflow_id: UUID, skip_approval: bool = False) -> Any:
        if node.node_type == "tool":
            return await self._run_tool(node, user_id, workflow_id, skip_approval=skip_approval)
        elif node.node_type == "condition":
            # Condition nodes usually just return the status of a previous tool
            # or evaluate their own logic. For now, we return context of previous node
            # or the arguments themselves.
            return node.arguments
        elif node.node_type == "delay":
            delay_seconds = node.arguments.get("seconds", 0)
            await asyncio.sleep(delay_seconds)
            return True
        elif node.node_type == "approval":
            # Native support for approval nodes could go here
            return True
        return None

    def _evaluate_condition(self, condition: Optional[str], node_result: Any) -> bool:
        """
        Evaluates if an edge's condition matches the result of the previous node.
        """
        if not condition:
            return True # Fallback edge
            
        if isinstance(node_result, dict):
            # Check if condition exists as a key or a value in 'status'
            status = node_result.get("status", "").lower()
            return condition.lower() == status or condition.lower() in str(node_result).lower()
        
        return condition.lower() in str(node_result).lower()

    async def _run_tool(self, node: WorkflowNode, user_id: UUID, workflow_id: UUID, skip_approval: bool = False) -> Any:
        tool_name = node.tool
        if not tool_name:
            raise Exception(f"Tool name missing for node {node.id}")

        tool = get_tool_by_name(tool_name)
        if not tool:
            raise Exception(f"Tool {tool_name} not found")

        # Prepare arguments (Resolve variables from context)
        args = self._resolve_arguments(node.arguments)
        
        # High Stake Check
        # Skip approval if:
        # 1. We are resuming from a previous approval (skip_approval is True)
        # 2. It's a manual execution (The user clicking 'Execute' IS the approval)
        # 3. It's a scheduled execution and the workflow is already 'Active' (User has authorized the automation)
        
        is_manual = self.execution_type == "manual"
        is_active_scheduled = self.execution_type == "scheduled" and workflow.is_active
        
        if not skip_approval and is_approval_required(tool_name) and not is_manual and not is_active_scheduled:
            from app.db.models.pending_action import PendingAction
            
            action_type = "automation_approval" if self.execution_type == "scheduled" else "tool_approval"
            
            pending_action = PendingAction(
                workflow_id=workflow_id,
                execution_id=self.execution_id,
                node_id=node.id,
                user_id=user_id,
                tool_name=tool_name,
                tool_args=args, # Only serializable args
                status="awaiting_approval"
            )
            
            self.session.add(pending_action)
            await self.session.commit()

            # Pause the execution
            execution = await self.session.get(WorkflowExecution, self.execution_id)
            if execution:
                execution.current_node_id = node.id
                execution.context = self.context
                execution.status = "paused"
                self.session.add(execution)
                await self.session.commit()
            
            raise Exception(f"Execution PAUSED for {action_type}. Approval ID: {pending_action.id}")

        # Inject transient arguments for actual execution
        full_args = {**args}
        full_args['session'] = self.session
        full_args['user_id'] = user_id

        try:
            # Execute Tool
            result = await tool.ainvoke(full_args)
            self.context[str(node.id)] = result
            return result
        except Exception as e:
            raise Exception(f"Error in tool {tool_name}: {str(e)}")

    def _resolve_arguments(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively resolve placeholders in arguments using the current execution context.
        Example: {{node_123.emails[0].subject}}
        """
        def resolve_value(v):
            if isinstance(v, str) and v.startswith("{{") and v.endswith("}}"):
                path_str = v[2:-2].strip()
                # Split by dots, but handle brackets if we wanted to be super fancy
                # For now, just dot notation
                parts = path_str.split(".")
                
                source_node_id = parts[0]
                if source_node_id not in self.context:
                    return v # Return as is if source not found
                
                current = self.context[source_node_id]
                for part in parts[1:]:
                    try:
                        if isinstance(current, dict):
                            current = current.get(part)
                        elif isinstance(current, list):
                            current = current[int(part)]
                        else:
                            current = getattr(current, part)
                    except:
                        return v # Fail gracefully
                return current
            
            if isinstance(v, dict):
                return {ik: resolve_value(iv) for ik, iv in v.items()}
            if isinstance(v, list):
                return [resolve_value(iv) for iv in v]
            return v

        return {k: resolve_value(v) for k, v in arguments.items()}
