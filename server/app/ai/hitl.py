from uuid import UUID

from app.db.crud.crud_pending_action import update_pending_action_status
from app.agent.tools import is_approval_required
from app.services.approval_service import (
    create_pending_action_service,
    get_latest_pending_action_service,
    delete_pending_action
)

def requires_approval(tool_name: str) -> bool:
    return is_approval_required(tool_name)


from app.agent.approval_llm import generate_approval_message

async def create_approval_request(
    *,
    session,
    chat_id,
    user_id,
    tool_name,
    tool_args,
) -> str:
    action = await create_pending_action_service(
        session=session,
        chat_id=chat_id,
        user_id=user_id,
        tool_name=tool_name,
        tool_args=tool_args,
    )

    # Return a special tag that the frontend can parse to show buttons
    return f"\n\n[ACTION_ID:{action.id}:{tool_name}]\n"



async def resolve_approval(
    *,
    session,
    chat_id: UUID,
    user_input: str,
):
    action = await get_latest_pending_action_service(session, chat_id)

    if not action:
        return None

    from app.agent.intent_classifier import classify_approval_intent

    # Use LLM to classify intent
    decision = await classify_approval_intent(user_input)

    if decision == "approved":
        await update_pending_action_status(session, action, "approved")
        return action

    if decision == "rejected":
        # Don't delete yet, mark as rejected so Executor can report it
        await update_pending_action_status(session, action, "rejected")
        return "rejected"

    return "invalid"


