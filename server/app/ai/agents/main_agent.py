from typing import AsyncGenerator, List, Optional, Any
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from app.ai.agents.base import BaseAgent
from app.ai.agents.planner_agent import PlannerAgent
from app.ai.agents.memory_agent import MemoryAgent
import json

class MainAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            model_name="gpt-4o",
            temperature=0.7, # Slightly higher for better conversational flow
            system_prompt="You are Taskमित्र (TaskMitra), an Agentic AI Assistant. You help users automate their workflows across Google Workspace and GitHub. You can chat naturally, but if the user wants to automate something, you will invoke the Planner."
        )
        self.planner = PlannerAgent()
        self.memory_agent = MemoryAgent()

    async def run(
        self, 
        user_input: str, 
        session: Any,
        user_id: Any,
        chat_id: Any,
        chat_history: List[BaseMessage] = []
    ) -> AsyncGenerator[str, None]:
        
        # 1. Classify Intent (With Robustness Check)
        from app.schemas.intent_schema import MainAgentIntent
        from datetime import datetime
        import pytz
        system_time = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S (%A)")
        
        classification_prompt = f"""
        System Time: {system_time}
        
        Analyze the user's input and determine if they want to 'chat' or perform a 'task'.
        
        A 'task' is robust ONLY if it has all required info:
        - If scheduling: needs a specific time/date (not just 'later').
        - If email: needs a recipient or clear subject.
        - If drive/github: needs a file/repo name.
        
        If information is missing, set intent='clarify' and provide a 'clarification_question'.
        """
        
        intent_decision: MainAgentIntent = await self.get_structured_output(
            output_schema=MainAgentIntent,
            user_input=f"CLASSIFY THIS: {user_input}\n\nSYSTEM_CONTEXT: {classification_prompt}",
            chat_history=chat_history
        )
        
        # 2. Check for Long-term Memory retrieval
        retrieved_context = ""
        if intent_decision.needs_memory:
            try:
                from app.services.memory_service import MemoryService
                memory_service = MemoryService()
                memories = await memory_service.search_memory(
                    session=session,
                    user_id=user_id,
                    query=intent_decision.search_query or user_input,
                    limit=3
                )
                if memories:
                    retrieved_context = "\n\nRelevant past information you should know:\n" + \
                        "\n".join([f"- {m.content}" for m in memories])
            except Exception as e:
                print(f"Memory Retrieval Error: {e}")

        # 3. Decision Path
        if intent_decision.intent == "clarify":
            yield intent_decision.clarification_question or "Could you provide more details about that request?"
            return

        elif intent_decision.intent == "task":
            yield "I'm planning that workflow for you now... 🛠️\n"
            
            # Use the task description from the classifier
            actual_task_request = intent_decision.task_description or user_input
                
            # 1. Generate the plan
            from app.schemas.workflow_graph import WorkflowGraphStructuredOutput
            from app.services.workflow_service import orchestrate_ai_workflow
            
            plan: WorkflowGraphStructuredOutput = await self.planner.plan_workflow(actual_task_request, context=retrieved_context)
            
            # 2. Persist to DB using Modular Service
            new_workflow = await orchestrate_ai_workflow(
                session=session,
                user_id=user_id,
                chat_id=chat_id,
                plan=plan
            )

            msg = f"Done! I've created a new workflow: **{plan.workflow_name}**."
            if plan.trigger.type == "scheduled":
                msg += f"\n\n **Note:** Since this is a scheduled workflow, I've paused it for your security. Please **approve the automation** below to activate the schedule. [WORKFLOW_ID:{new_workflow.id}:{plan.workflow_name}]"
            else:
                # Trigger Immediate Execution
                from app.tasks.workflow_tasks import execute_workflow_task
                execute_workflow_task.delay(str(new_workflow.id), str(user_id))
                
                msg += f" I've started the execution for you! I'm taking you to the Workflow Studio now to see it in action. [REDIRECT_TO:/workflow/chat/{chat_id}]"
            
            yield msg

        else:
            # Chat Intent
            full_system_prompt = self.system_prompt
            if retrieved_context:
                full_system_prompt += f"\n\n[PAST CONTEXT]{retrieved_context}\n[END PAST CONTEXT]\nUse this context ONLY if it's relevant to the current query."

            async for chunk in self.llm.astream([("system", full_system_prompt)] + chat_history + [("user", user_input)]):
                yield chunk.content

        # 4. Memory Persistence (Run for both Chat and Task turns)
        try:
            from app.services.memory_service import MemoryService
            memory_service = MemoryService()
            
            memory_decision = await self.memory_agent.analyze_memory(user_input)
            if memory_decision.should_save:
                await memory_service.add_memory(
                    session=session,
                    user_id=user_id,
                    content=memory_decision.extracted_information,
                    metadata={"category": memory_decision.category, "original_query": user_input}
                )
        except Exception as e:
            print(f"Memory Agent Error: {e}")
