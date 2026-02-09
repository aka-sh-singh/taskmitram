from datetime import datetime, timezone
from typing import Dict, List
from uuid import UUID
from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.crud.crud_integrations import is_connected
from app.integrations.google import (
    GMAIL_PROVIDER,
    DRIVE_PROVIDER,
    SHEETS_PROVIDER,
    build_google_oauth_url,
    connect_user_google,
    disconnect_user_google
)
from app.integrations.github import (
    GITHUB_PROVIDER,
    build_github_oauth_url,
    connect_user_github,
    disconnect_user_github
)
from app.schemas.integrations_schema import IntegrationStatus, IntegrationStatusResponse, ConnectURLResponse, OAuthSuccess, DisconnectResponse

from app.db.crud.crud_integrations import get_token

async def get_all_integration_statuses_service(
    session: AsyncSession, 
    user_id: UUID
) -> IntegrationStatusResponse:
    """
    Returns the connection status for all supported integrations.
    A connection is only considered 'active' if it has a valid token 
    or a refresh token that allows future use.
    """
    providers = [GMAIL_PROVIDER, DRIVE_PROVIDER, SHEETS_PROVIDER, GITHUB_PROVIDER]
    status_dict = {}
    
    now = datetime.now(timezone.utc)
    
    for provider in providers:
        token = await get_token(session, user_id, provider)
        
        is_active = False
        if token:
            # If it's a permanent token (like GitHub often is) or not yet expired
            if not token.expires_at or token.expires_at > now:
                is_active = True
            # If it IS expired but we have a refresh token, we consider it connected 
            # because the agent will auto-heal it on the next command.
            elif token.refresh_token:
                is_active = True
                
        status_dict[provider] = IntegrationStatus(
            provider=provider,
            connected=is_active
        )
        
    return IntegrationStatusResponse(status=status_dict)

async def get_google_connect_url_service(provider: str) -> ConnectURLResponse:
    """
    Builds the OAuth URL for the specified Google provider.
    """
    url = build_google_oauth_url(provider)
    return ConnectURLResponse(auth_url=url)

async def connect_google_user_service(
    session: AsyncSession, 
    user_id: UUID, 
    code: str, 
    provider: str
) -> OAuthSuccess:
    """
    Exchanges OAuth code for tokens and saves them in the database.
    """
    try:
        await connect_user_google(session, user_id, code, provider)
        return OAuthSuccess(provider=provider, status="connected")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to connect {provider} account: {str(e)}")

async def disconnect_google_user_service(
    session: AsyncSession, 
    user_id: UUID, 
    provider: str
) -> DisconnectResponse:
    """
    Revokes the token and removes it from the database.
    """
    success = await disconnect_user_google(session, user_id, provider)
    if not success:
        raise HTTPException(status_code=404, detail=f"No {provider} integration found for this user.")
        
    return DisconnectResponse(provider=provider, status="disconnected")

# GITHUB SERVICES

async def get_github_connect_url_service() -> ConnectURLResponse:
    return ConnectURLResponse(auth_url=build_github_oauth_url())

async def connect_github_user_service(
    session: AsyncSession, 
    user_id: UUID, 
    code: str
) -> OAuthSuccess:
    try:
        await connect_user_github(session, user_id, code)
        return OAuthSuccess(provider=GITHUB_PROVIDER, status="connected")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to connect GitHub account: {str(e)}")

async def disconnect_github_user_service(
    session: AsyncSession, 
    user_id: UUID
) -> DisconnectResponse:
    success = await disconnect_user_github(session, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="No GitHub integration found for this user.")
        
    return DisconnectResponse(provider=GITHUB_PROVIDER, status="disconnected")
