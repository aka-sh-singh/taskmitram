from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel

from app.db.session import get_session
from app.core.deps import get_current_user
from app.schemas.integrations_schema import (
    ConnectURLResponse,
    OAuthSuccess,
    DisconnectResponse,
)
from app.services.integration_service import (
    get_github_connect_url_service,
    connect_github_user_service,
    disconnect_github_user_service
)

router = APIRouter(prefix="/integrations/github", tags=["Integrations - GitHub"])

class GithubExchangeRequest(BaseModel):
    code: str

@router.get("/connect", response_model=ConnectURLResponse)
async def connect_github():
    return await get_github_connect_url_service()

@router.post("/exchange", response_model=OAuthSuccess)
async def github_exchange_code(
    payload: GithubExchangeRequest,
    session: AsyncSession = Depends(get_session),
    user = Depends(get_current_user)
):
    return await connect_github_user_service(session, user.id, payload.code)

@router.delete("/disconnect", response_model=DisconnectResponse)
async def disconnect_github(
    session: AsyncSession = Depends(get_session),
    user = Depends(get_current_user)
):
    return await disconnect_github_user_service(session, user.id)
