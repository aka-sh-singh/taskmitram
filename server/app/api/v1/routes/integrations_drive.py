from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.db.session import get_session
from app.schemas.integrations_schema import (
    ConnectURLResponse,
    OAuthSuccess,
    DisconnectResponse,
)
from app.services.integration_service import (
    get_google_connect_url_service,
    connect_google_user_service,
    disconnect_google_user_service
)
from app.integrations.google import DRIVE_PROVIDER

router = APIRouter(prefix="/integrations/google/drive", tags=["Integrations - Google Drive"])

# A simple schema for the POST request body
class GoogleExchangeRequest(BaseModel):
    code: str

# 1) Connect - Get Google OAuth URL
@router.get("/connect", response_model=ConnectURLResponse)
async def connect_google_drive():
    return await get_google_connect_url_service(DRIVE_PROVIDER)


# 2) Exchange - Frontend sends the code here
@router.post("/exchange", response_model=OAuthSuccess)
async def google_drive_exchange_code(
    payload: GoogleExchangeRequest,
    session: AsyncSession = Depends(get_session),
    user = Depends(get_current_user)
):
    return await connect_google_user_service(session, user.id, payload.code, DRIVE_PROVIDER)


# 3) Disconnect - remove stored token
@router.delete("/disconnect", response_model=DisconnectResponse)
async def disconnect_google_drive(
    session: AsyncSession = Depends(get_session),
    user = Depends(get_current_user)
):
    return await disconnect_google_user_service(session, user.id, DRIVE_PROVIDER)
