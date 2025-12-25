from uuid import UUID

from app.db.crud.crud_pending_action import (
    create_pending_action,
    get_pending_action,
    update_pending_action_status,
    delete_pending_action,
)

HIGH_RISK_TOOLS = {
    "send_gmail",
}


def requires_approval(tool_name: str) -> bool:
    return tool_name in HIGH_RISK_TOOLS


from app.agent.approval_llm import generate_approval_message

async def create_approval_request(
    *,
    session,
    chat_id,
    user_id,
    tool_name,
    tool_args,
) -> str:
    action = await create_pending_action(
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
    action = await get_pending_action(session, chat_id)

    if not action:
        return None

    from app.agent.intent_classifier import classify_approval_intent

    # Use LLM to classify intent
    decision = await classify_approval_intent(user_input)

    if decision == "approved":
        await update_pending_action_status(session, action, "approved")
        return action

    if decision == "rejected":
        # First mark as rejected in DB (optional, but good for logs), then delete or keep as rejected
        # Your previous logic deleted it immediately upon rejection
        await update_pending_action_status(session, action, "rejected")
        await delete_pending_action(session, action)
        return "rejected"

    return "invalid"


