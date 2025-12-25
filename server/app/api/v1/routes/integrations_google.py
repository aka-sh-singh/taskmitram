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
from app.services.integrations.google import (
    build_google_oauth_url,
    connect_user_google,
    disconnect_user_google,
    PROVIDER_NAME
)

router = APIRouter(prefix="/integrations/google", tags=["Integrations - Google"])

# A simple schema for the POST request body
class GoogleExchangeRequest(BaseModel):
    code: str

# 1) Connect - Get Google OAuth URL
@router.get("/connect", response_model=ConnectURLResponse)
async def connect_google():
    """
    Step 1: Frontend calls this to get the URL to redirect the user to Google.
    """
    url = build_google_oauth_url()
    return ConnectURLResponse(auth_url=url)


# 2) Exchange - Frontend sends the code here
@router.post("/exchange", response_model=OAuthSuccess)
async def google_exchange_code(
    payload: GoogleExchangeRequest,
    session: AsyncSession = Depends(get_session),
    user = Depends(get_current_user)
):
    """
    Step 2: After Google redirects to the FRONTEND, the frontend grabs 
    the 'code' from the URL and POSTS it here.
    
    Since this is a standard API call from your frontend, 
    Depends(get_current_user) will now work correctly!
    """
    try:
        await connect_user_google(session, user.id, payload.code)
        return OAuthSuccess(provider=PROVIDER_NAME, status="connected")
    except Exception as e:
        # Log the error here
        raise HTTPException(status_code=400, detail=f"Failed to connect Google account: {str(e)}")


# 3) Disconnect - remove stored token
@router.delete("/disconnect", response_model=DisconnectResponse)
async def disconnect_google(
    session: AsyncSession = Depends(get_session),
    user = Depends(get_current_user)
):
    """
    Removes the user's Google tokens from the database.
    """
    success = await disconnect_user_google(session, user.id)
    if not success:
        raise HTTPException(status_code=404, detail="No Google integration found for this user.")
        
    return DisconnectResponse(provider=PROVIDER_NAME, status="disconnected")