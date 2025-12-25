from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


# USER SIGNUP SCHEMA
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


# USER LOGIN SCHEMA
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# USER RESPONSE SCHEMA (Safe to return)
class UserRead(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True   # Allows ORM → schema conversion

class UpdateUsername(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)


class ChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)




# TOKEN RESPONSE SCHEMA
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# REFRESH TOKEN REQUEST SCHEMA
class RefreshTokenRequest(BaseModel):
    refresh_token: str
