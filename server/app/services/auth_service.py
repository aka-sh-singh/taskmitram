from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.crud.crud_user import (
    create_user,
    delete_all_user_tokens,
    get_user_by_email,
    get_user_by_username,
    store_refresh_token,
    get_refresh_token,
    delete_refresh_token,
)

from app.db.models.user import User
from app.schemas.user_schema import UserCreate, UserLogin, TokenResponse, RefreshTokenRequest
from app.core.security import hash_password, verify_password
from app.core.jwt import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.core.config import jwtconfig



# SIGNUP SERVICE
async def signup_service(session: AsyncSession, data: UserCreate) -> TokenResponse:
    
    existing_email = await get_user_by_email(session, data.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered.")

    
    existing_username = await get_user_by_username(session, data.username)
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken.")


    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
    )

    new_user = await create_user(session, user)

    access_token = create_access_token(str(new_user.id))
    refresh_token = create_refresh_token(str(new_user.id))

    
    expires_at = datetime.now(timezone.utc) + timedelta(days=jwtconfig.REFRESH_TOKEN_EXPIRE_DAYS)
    await store_refresh_token(session, new_user.id, refresh_token, expires_at)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


# LOGIN SERVICE
async def login_service(session: AsyncSession, data: UserLogin) -> TokenResponse:

    user = await get_user_by_email(session, data.email)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password.")


    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password.")


    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    
    expires_at = datetime.now(timezone.utc) + timedelta(days=jwtconfig.REFRESH_TOKEN_EXPIRE_DAYS)
    await store_refresh_token(session, user.id, refresh_token, expires_at)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )



# app/services/auth_service.py

from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.jwt import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)

from app.core.config import jwtconfig
from app.db.crud.crud_user import (
    get_refresh_token,
    delete_refresh_token,
    store_refresh_token,
)


async def refresh_token_service(session: AsyncSession, data) -> dict:
    """
    Secure, atomic refresh token rotation.
    Steps:
    1. Decode incoming refresh token
    2. Check existence in DB
    3. Check expiry
    4. Delete old token (commit=False)
    5. Create & store new token (commit=False)
    6. session.commit() → atomic operation
    """

    # 1. Decode refresh token
    payload = decode_refresh_token(data.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token.")

    user_id = payload.sub

    # 2. Ensure token exists in DB
    stored = await get_refresh_token(session, data.refresh_token)
    if not stored:
        raise HTTPException(status_code=401, detail="Refresh token not recognized.")

    # 3. Check expiry
    if stored.expires_at < datetime.now(timezone.utc):
        # remove expired token
        await delete_refresh_token(session, data.refresh_token, commit=True)
        raise HTTPException(status_code=401, detail="Refresh token expired.")

    # 4. Generate new tokens
    new_access_token = create_access_token(user_id)
    new_refresh_token = create_refresh_token(user_id)

    expires_at = datetime.now(timezone.utc) + timedelta(
        days=jwtconfig.REFRESH_TOKEN_EXPIRE_DAYS
    )

    try:
        # 5. Delete old token (but DO NOT COMMIT)
        await delete_refresh_token(session, data.refresh_token, commit=False)

        # 6. Insert new refresh token (but DO NOT COMMIT)
        await store_refresh_token(
            session,
            user_id,
            new_refresh_token,
            expires_at,
            commit=False
        )

        # 7. Commit delete + insert together (ATOMIC)
        await session.commit()

    except Exception:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Failed to rotate refresh token.")

    # 8. Return new tokens
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
    }




# LOGOUT SERVICE
async def logout_service(session: AsyncSession, refresh_token: str) -> None:
    await delete_refresh_token(session, refresh_token)
