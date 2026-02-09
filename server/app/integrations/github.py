import httpx
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple
from uuid import UUID

from app.core.config import integrationsettings
from app.db.crud.crud_integrations import (
    get_token,
    create_or_update_token,
    delete_token
)
from sqlmodel.ext.asyncio.session import AsyncSession

# CONSTANTS
GITHUB_AUTH_BASE = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_ENDPOINT = "https://github.com/login/oauth/access_token"
GITHUB_PROVIDER = "github"

# BUILD GITHUB OAUTH URL
def build_github_oauth_url() -> str:
    import urllib.parse

    params = {
        "client_id": integrationsettings.GITHUB_CLIENT_ID,
        "redirect_uri": integrationsettings.GITHUB_REDIRECT_URI,
        "scope": integrationsettings.GITHUB_SCOPES,
        "state": GITHUB_PROVIDER,
    }

    query = urllib.parse.urlencode(params)
    return f"{GITHUB_AUTH_BASE}?{query}"


# EXCHANGE CODE FOR TOKENS
async def exchange_github_code_for_token(code: str) -> str:
    async with httpx.AsyncClient(timeout=10) as client:
        data = {
            "client_id": integrationsettings.GITHUB_CLIENT_ID,
            "client_secret": integrationsettings.GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": integrationsettings.GITHUB_REDIRECT_URI,
        }
        headers = {"Accept": "application/json"}

        response = await client.post(GITHUB_TOKEN_ENDPOINT, data=data, headers=headers)
        response.raise_for_status()

        token_data = response.json()
        
        # GitHub returns 'access_token' (no refresh_token usually for simple OAuth apps)
        access_token = token_data.get("access_token")
        if not access_token:
            raise Exception(f"GitHub OAuth error: {token_data.get('error_description', 'No access token')}")
            
        return access_token


# CONNECT USER
async def connect_user_github(
    session: AsyncSession,
    user_id: UUID,
    code: str
):
    access_token = await exchange_github_code_for_token(code)

    token = await create_or_update_token(
        session=session,
        user_id=user_id,
        provider=GITHUB_PROVIDER,
        access_token=access_token,
        refresh_token=None,  # GitHub OAuth tokens are permanent until revoked
        scopes=integrationsettings.GITHUB_SCOPES,
        expires_at=None      # Permanent
    )

    return token


# DISCONNECT USER
async def disconnect_user_github(
    session: AsyncSession,
    user_id: UUID
):
    # GitHub doesn't have a standard REST revoke endpoint like Google for simple OAuth apps 
    # (Revocation usually happens via the GitHub UI by the user or via a specialized API)
    # So we just delete it locally.
    return await delete_token(session, user_id, GITHUB_PROVIDER)


# AGENT VALIDATOR
async def validate_github_capability(
    session: AsyncSession, 
    user_id: UUID, 
    required_scope_substring: str
) -> Dict:
    token_entry = await get_token(session, user_id, GITHUB_PROVIDER)
    
    if not token_entry:
        return {
            "authorized": False, 
            "error": "Your GitHub account is not connected. Please go to Settings and 'Connect' your GitHub account."
        }

    # Simplified scope check
    # GitHub scopes are strings like 'repo user'
    user_scopes = token_entry.scopes or ""
    
    if required_scope_substring not in user_scopes:
        return {
            "authorized": False, 
            "error": f"Your GitHub connection is missing the '{required_scope_substring}' permission. Please disconnect and reconnect to grant all required permissions."
        }

    return {
        "authorized": True, 
        "access_token": token_entry.access_token
    }
