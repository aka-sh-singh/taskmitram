from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.user_schema import UserCreate, UserLogin, TokenResponse, RefreshTokenRequest
from app.services.auth_service import (
    signup_service,
    login_service,
    refresh_token_service,
    logout_service,
)


router = APIRouter(prefix="/auth", tags=["Auth"])



# SIGNUP ENDPOINT
@router.post("/signup", response_model=TokenResponse)
async def signup(data: UserCreate, session: AsyncSession = Depends(get_session)):
    return await signup_service(session, data)



# LOGIN ENDPOINT
@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, session: AsyncSession = Depends(get_session)):
    return await login_service(session, data)



# REFRESH TOKEN ENDPOINT
@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest, session: AsyncSession = Depends(get_session)):
    return await refresh_token_service(session, data)




@router.post("/logout")
async def logout(data: RefreshTokenRequest, session: AsyncSession = Depends(get_session)):
    """
    Logout only deletes the specific refresh token.
    This logs out the current device/session only.
    """
    await logout_service(session, data.refresh_token)
    return {"message": "Logged out successfully."}
