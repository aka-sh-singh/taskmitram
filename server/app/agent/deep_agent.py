from uuid import UUID
from typing import List, AsyncGenerator
import json

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

from app.agent.utils import to_langchain_messages
from app.agent.hitl import (
    requires_approval,
    create_approval_request,
)
from app.db.crud.crud_pending_action import (
    get_pending_action,
    delete_pending_action,
)


# TOOL REGISTRY
from app.agent.tools import ALL_TOOLS as TOOLS, TOOLS_REQUIRING_APPROVAL, is_approval_required, get_tool_by_name


# SYSTEM PROMPT
SYSTEM_PROMPT = """
You are TASKमित्र (Task Mitra), a highly capable AI assistant.

Your capabilities:
1. Summarize text.
2. Fetch and manage Gmail emails (read, search, send, check delivery).
3. Google Drive: List files, read text/doc content, and create new files.
4. Google Sheets: Read cell ranges, update/overwrite values, append rows to tables, and create new spreadsheets.
5. GitHub: List repositories, read file contents, browse issues, and create new issues.
6. Help with general tasks and information.

Rules of Engagement:
- When a tool is called, you will receive its output in the next turn. 
- Use the data provided by the tools to answer the user's request. 
- PRESENT DATA CLEARLY: Use tables for sheet data/issue lists and structured markdown for file lists or email bodies.
- **CRITICAL**: DO NOT wrap content in global code blocks (```) or black containers. Treat the text as part of your direct conversational response.
- High-risk actions (sending emails, creating/modifying files, sheets, or issues) ALWAYS require user approval via the HITL system.
- **CONTEXT**: Before reading a file or list issues, ensure you have the correct 'owner' and 'repo' name. Use 'list_github_repositories' if you are unsure about the exact repository name.
- Be proactive but always polite and concise.
"""


# LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2,
)

llm_with_tools = llm.bind_tools(TOOLS)



# main entry point
async def run_deep_agent(
    *,
    chat_id: UUID,
    user_input: str,
    chat_messages: List,
    user_id: UUID,
    session,
) -> AsyncGenerator[str, None]:
    """
    Executes the conversational DeepAgent with HITL support and streaming.
    """


    pending = await get_pending_action(session, chat_id)



    history = to_langchain_messages(chat_messages)
    
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + history
    

    messages.append(HumanMessage(content=user_input))



    max_steps = 5
    for _ in range(max_steps):
        full_msg = None
        

        async for chunk in llm_with_tools.astream(messages):
            if full_msg is None:
                full_msg = chunk
            else:
                full_msg += chunk
            

            if not getattr(chunk, 'tool_call_chunks', []) and chunk.content:
                yield chunk.content

        messages.append(full_msg)

        if not full_msg.tool_calls:
            return

        # Handle Tool Calls
        for tool_call in full_msg.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]


            pending = await get_pending_action(session, chat_id)
            
            is_approved = False
            if is_approval_required(tool_name):
                if pending and pending.status == "approved" and pending.tool_name == tool_name:
                    is_approved = True
                    tool_args = pending.tool_args
                
                if not is_approved:
                    yield await create_approval_request(
                        session=session,
                        chat_id=chat_id,
                        user_id=user_id,
                        tool_name=tool_name,
                        tool_args=tool_args,
                    )
                    return

            # EXECUTE TOOL
            selected_tool = get_tool_by_name(tool_name)
            
            tool_output = "Error: Tool not found."
            if selected_tool:
                execution_args = {**tool_args}
                if selected_tool.args_schema:
                    schema_fields = selected_tool.args_schema.model_fields
                    if "session" in schema_fields:
                        execution_args["session"] = session
                    if "user_id" in schema_fields:
                        execution_args["user_id"] = user_id
                
                try:
                    tool_output = await selected_tool.ainvoke(execution_args)
                    
                    if is_approved and pending:
                        await delete_pending_action(session, pending)
                        pending = None 
                        
                except Exception as e:
                    tool_output = f"Error executing tool: {e}"
            
            # Append Tool Message
            messages.append(ToolMessage(
                content=str(tool_output), 
                tool_call_id=tool_id,
                name=tool_name
            ))

    yield "Agent step limit reached."
