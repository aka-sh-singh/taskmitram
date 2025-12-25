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


# TOOLS
from app.agent.tools.basic_tools import summarize_text,current_user_id
# TOOL DEFINITIONS
from app.agent.tools.gmail_tools import send_gmail, fetch_recent_gmail, read_gmail_message, verify_delivery

# Tools that require Human-in-the-loop approval
TOOLS_REQUIRING_APPROVAL = ["send_gmail"]

TOOLS = [
    summarize_text,
    current_user_id,
    send_gmail,
    fetch_recent_gmail,
    read_gmail_message,
    verify_delivery,
]


# SYSTEM PROMPT
SYSTEM_PROMPT = """
You are TASKमित्र (Task Mitra), a highly capable AI assistant.

Your capabilities:
1. Summarize text.
2. Fetch and manage Gmail emails.
3. Verify if emails were successfully delivered or bounced.
4. Help with general tasks and information.

Rules of Engagement:
- When a tool is called, you will receive its output in the next turn. 
- Use the data provided by the tools to answer the user's request. 
- PRESENT EMAILS CLEARLY: When displaying an email body, use natural markdown for formatting (e.g., # for headers, ** for importance, > for quotes). 
- **CRITICAL**: DO NOT wrap the email body in code blocks (```) or black containers. Treat the email text as part of your direct conversational response.
- High-risk actions (like sending emails) ALWAYS require user approval via the HITL system.
- **DELIVERY CHECKS**: If you send an email to a suspicious or nonsensical address (like 'abc@xyz.com'), warn the user that it might bounce. If asked to check if an email arrived, use the 'verify_delivery' tool to look for bounce-back messages from the mailer-daemon.
- Be proactive but always polite and concise.
"""


# LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2,
)

llm_with_tools = llm.bind_tools(TOOLS)



# MAIN ENTRY POINT
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

    # 1. HITL Check: See if we have an approved action waiting to be executed
    pending = await get_pending_action(session, chat_id)
    # If the action is already approved via button, we will use it in the loop below.
    # We only care about it if it's 'approved'. If it's 'awaiting_approval', we pause later.

    # 2. Build conversation history
    history = to_langchain_messages(chat_messages)
    
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + history
    
    # Append current input if not already in history
    messages.append(HumanMessage(content=user_input))


    # 3. Agent Loop (Manual Execution with Streaming)
    max_steps = 5
    for _ in range(max_steps):
        full_msg = None
        
        # Invoke LLM with streaming
        async for chunk in llm_with_tools.astream(messages):
            if full_msg is None:
                full_msg = chunk
            else:
                full_msg += chunk
            
            # Yield content chunks only if this chunk doesn't start a tool call
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

            # HITL CHECK: Re-verify status from database to avoid stale reads
            pending = await get_pending_action(session, chat_id)
            
            is_approved = False
            if requires_approval(tool_name):
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
            selected_tool = next((t for t in TOOLS if t.name == tool_name), None)
            
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
