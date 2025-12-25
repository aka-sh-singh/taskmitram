from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_session
from app.db.models.user import User

from app.schemas.user_schema import UserRead, UpdateUsername, ChangePassword
from app.db.crud.crud_user import get_user_by_username
from app.core.security import hash_password, verify_password

router = APIRouter(prefix="/users", tags=["Users"])


#GET CURRENT USER PROFILE
@router.get("/me", response_model=UserRead)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user


#UPDATE USERNAME
@router.patch("/update-username", response_model=UserRead)
async def update_username(
    data: UpdateUsername,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    
    existing = await get_user_by_username(session, data.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")


    current_user.username = data.username
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)

    return current_user


#CHANGE PASSWORD
@router.patch("/change-password")
async def change_password(
    data: ChangePassword,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):


    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")


    current_user.hashed_password = hash_password(data.new_password)
    session.add(current_user)
    await session.commit()

    return {"message": "Password changed successfully"}
