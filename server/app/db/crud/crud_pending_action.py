from datetime import datetime, timezone
from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.models.pending_action import PendingAction


async def create_pending_action(
    session: AsyncSession,
    *,
    chat_id: UUID,
    user_id: UUID,
    tool_name: str,
    tool_args: dict,
):
    action = PendingAction(
        chat_id=chat_id,
        user_id=user_id,
        tool_name=tool_name,
        tool_args=tool_args,
    )
    session.add(action)
    await session.commit()
    await session.refresh(action)
    return action


async def get_pending_action(
    session: AsyncSession,
    chat_id: UUID,
):
    # Fetch the latest action that is either awaiting approval or already approved
    # We prioritize 'approved' status to make sure the agent picks it up immediately.
    stmt = (
        select(PendingAction)
        .where(PendingAction.chat_id == chat_id)
        .where(PendingAction.status.in_(["awaiting_approval", "approved"]))
        # Status 'approved' should come before 'awaiting_approval' if multiple exist for some reason
        .order_by(PendingAction.status.desc(), PendingAction.created_at.desc())
    )
    res = await session.exec(stmt)
    return res.first()


async def update_pending_action_status(
    session: AsyncSession,
    action: PendingAction,
    status: str,
):
    action.status = status
    session.add(action)
    await session.commit()
    await session.refresh(action)
    return action


async def delete_pending_action(
    session: AsyncSession,
    action: PendingAction,
):
    await session.delete(action)
    await session.commit()
