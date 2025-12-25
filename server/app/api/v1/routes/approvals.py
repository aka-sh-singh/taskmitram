from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.db.models.user import User
from app.core.deps import get_current_user
from app.db.crud.crud_pending_action import (
    get_pending_action, 
    update_pending_action_status, 
    delete_pending_action
)
from app.db.models.pending_action import PendingAction
from sqlmodel import select

router = APIRouter()

@router.post("/{action_id}/approve")
async def approve_action(
    action_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Use session.get for faster and more reliable primary key lookup
    action = await session.get(PendingAction, action_id)

    if not action:
        raise HTTPException(status_code=404, detail="This action has already been processed or is no longer available.")
    
    if action.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to approve this action")

    await update_pending_action_status(session, action, "approved")
    return {"status": "success", "message": "Action approved."}

@router.post("/{action_id}/reject")
async def reject_action(
    action_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    stmt = select(PendingAction).where(PendingAction.id == action_id)
    res = await session.exec(stmt)
    action = res.first()

    if not action:
        raise HTTPException(status_code=404, detail="This action has already been processed or is no longer available.")
    
    if action.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await delete_pending_action(session, action)
    return {"status": "success", "message": "Action rejected and removed."}
