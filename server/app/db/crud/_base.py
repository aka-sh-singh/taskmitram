# app/db/crud/_base.py
from typing import Any, Dict
from sqlmodel.ext.asyncio.session import AsyncSession

async def create_and_commit(session: AsyncSession, obj):
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


# non-committing variant (safe to use inside session.begin())
async def create_no_commit(session: AsyncSession, obj: Any):
    session.add(obj)
    await session.flush()   # persist to DB within current transaction without committing
    return obj



async def delete_and_commit(session: AsyncSession, obj):
    await session.delete(obj)
    await session.commit()