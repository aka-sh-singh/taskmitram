from typing import Dict, Any, Optional
from uuid import UUID
from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.models.pending_action import PendingAction
from app.db.crud.crud_pending_action import (
    get_pending_action,
    update_pending_action_status,
    delete_pending_action,
    create_pending_action as crud_create_pending_action
)

async def create_pending_action_service(
    session: AsyncSession,
    chat_id: UUID,
    user_id: UUID,
    tool_name: str,
    tool_args: dict
) -> PendingAction:
    """
    Creates a new pending action that requires user approval.
    """
    return await crud_create_pending_action(
        session=session,
        chat_id=chat_id,
        user_id=user_id,
        tool_name=tool_name,
        tool_args=tool_args
    )

async def get_latest_pending_action_service(
    session: AsyncSession,
    chat_id: UUID
) -> Optional[PendingAction]:
    """
    Fetches the current pending action for a chat.
    """
    return await get_pending_action(session, chat_id)

async def approve_pending_action_service(
    session: AsyncSession,
    user_id: UUID,
    action_id: UUID
) -> Dict[str, str]:
    """
    Approves a pending action after verifying ownership.
    """
    action = await session.get(PendingAction, action_id)

    if not action:
        raise HTTPException(status_code=404, detail="Action not found or already processed.")
    
    if action.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to approve this action")

    await update_pending_action_status(session, action, "approved")
    return {"status": "success", "message": "Action approved."}

async def reject_pending_action_service(
    session: AsyncSession,
    user_id: UUID,
    action_id: UUID
) -> Dict[str, str]:
    """
    Rejects and deletes a pending action.
    """
    action = await session.get(PendingAction, action_id)

    if not action:
        raise HTTPException(status_code=404, detail="Action not found or already processed.")
    
    if action.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to reject this action")

    await delete_pending_action(session, action)
    return {"status": "success", "message": "Action rejected and removed."}
