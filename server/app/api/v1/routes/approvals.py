from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.db.models.user import User
from app.core.deps import get_current_user
from app.services.approval_service import (
    approve_pending_action_service,
    reject_pending_action_service
)

router = APIRouter()

@router.post("/{action_id}/approve")
async def approve_action(
    action_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await approve_pending_action_service(session, current_user.id, action_id)

@router.post("/{action_id}/reject")
async def reject_action(
    action_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await reject_pending_action_service(session, current_user.id, action_id)
