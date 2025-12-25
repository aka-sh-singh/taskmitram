from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid
from jose import jwt, JWTError
from pydantic import BaseModel
from app.core.config import jwtconfig


class TokenPayload(BaseModel):
    sub: str
    exp: int
    iat: int | None = None
    jti: str | None = None


def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=jwtconfig.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": user_id,
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
    }

    return jwt.encode(to_encode, jwtconfig.SECRET_KEY, algorithm=jwtconfig.ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=jwtconfig.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "sub": user_id,
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "jti": str(uuid.uuid4()),
    }

    return jwt.encode(to_encode, jwtconfig.REFRESH_SECRET_KEY, algorithm=jwtconfig.ALGORITHM)


def decode_access_token(token: str) -> Optional[TokenPayload]:
    try:
        payload = jwt.decode(
            token,
            jwtconfig.SECRET_KEY,
            algorithms=[jwtconfig.ALGORITHM],
        )
        return TokenPayload(**payload)
    except JWTError:
        return None


def decode_refresh_token(token: str) -> Optional[TokenPayload]:
    try:
        payload = jwt.decode(
            token,
            jwtconfig.REFRESH_SECRET_KEY,
            algorithms=[jwtconfig.ALGORITHM],
        )
        return TokenPayload(**payload)
    except JWTError:
        return None
