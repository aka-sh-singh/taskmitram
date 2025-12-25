from uuid import UUID
from typing import Optional, List
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.models.user import User
from app.db.models.refresh_token import RefreshToken



# CREATE USER
async def create_user(session: AsyncSession, user: User) -> User:
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user



# GET USER BY EMAIL
async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    query = select(User).where(User.email == email)
    result = await session.execute(query)
    return result.scalar_one_or_none()



# GET USER BY USERNAME
async def get_user_by_username(session: AsyncSession, username: str) -> Optional[User]:
    query = select(User).where(User.username == username)
    result = await session.execute(query)
    return result.scalar_one_or_none()



# GET USER BY ID
async def get_user_by_id(session: AsyncSession, user_id: UUID) -> Optional[User]:
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()



# STORE REFRESH TOKEN IN DB
async def store_refresh_token(session: AsyncSession, user_id: UUID, token: str, expires_at,commit:bool=True) -> RefreshToken:
    refresh_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    session.add(refresh_token)
    if commit:
        await session.commit()
        await session.refresh(refresh_token)
    return refresh_token



# GET REFRESH TOKEN FROM DB
async def get_refresh_token(session: AsyncSession, token: str) -> Optional[RefreshToken]:
    query = select(RefreshToken).where(RefreshToken.token == token)
    result = await session.execute(query)
    return result.scalar_one_or_none()



# DELETE REFRESH TOKEN (on logout or rotation)
async def delete_refresh_token(session: AsyncSession, token: str, commit:bool=True) -> None:
    stored = await get_refresh_token(session, token)
    if stored:
        await session.delete(stored)
    if commit:
        await session.commit()



# DELETE ALL USER REFRESH TOKENS (optional)
async def delete_all_user_tokens(session: AsyncSession, user_id: UUID) -> None:
    query = select(RefreshToken).where(RefreshToken.user_id == user_id)
    result = await session.execute(query)
    tokens: List[RefreshToken] = result.scalars().all()

    for t in tokens:
        await session.delete(t)

    await session.commit()
