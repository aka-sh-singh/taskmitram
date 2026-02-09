from typing import Dict
import httpx
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.core.config import integrationsettings
from app.db.crud.crud_integrations import (
    get_token,
    create_or_update_token,
    delete_token
)
from sqlmodel.ext.asyncio.session import AsyncSession



# CONSTANTS
GOOGLE_AUTH_BASE = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_REVOKE_ENDPOINT = "https://oauth2.googleapis.com/revoke"

PROVIDER_NAME = "google_gmail" # deprecated, use specific ones
GMAIL_PROVIDER = "google_gmail"
DRIVE_PROVIDER = "google_drive"
SHEETS_PROVIDER = "google_sheets"


# BUILD GOOGLE OAUTH URL
def build_google_oauth_url(provider: str = GMAIL_PROVIDER) -> str:
    import urllib.parse

    client_id = integrationsettings.GOOGLE_CLIENT_ID
    redirect_uri = integrationsettings.GOOGLE_REDIRECT_URI
    
    if provider == DRIVE_PROVIDER:
        scopes = integrationsettings.GOOGLE_DRIVE_SCOPES
    elif provider == SHEETS_PROVIDER:
        scopes = integrationsettings.GOOGLE_SHEETS_SCOPES
    else:
        scopes = integrationsettings.GOOGLE_GMAIL_SCOPES

    # Ensure scopes are a single space-separated string
    if isinstance(scopes, (list, tuple)):
        scope_str = " ".join(scopes)
    else:
        scope_str = str(scopes)

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": scope_str,
        "state": provider,
        "access_type": "offline",   # ensures refresh_token
        "prompt": "consent"         # ensures refresh_token every time
    }

    # Build query with explicit quoting so spaces -> %20
    query = "&".join(
        f"{urllib.parse.quote_plus(k)}={urllib.parse.quote(v, safe='')}"
        for k, v in params.items()
    )

    return f"{GOOGLE_AUTH_BASE}?{query}"


# ============================
# EXCHANGE CODE FOR TOKENS
# ============================

async def exchange_code_for_tokens(code: str, provider: str = GMAIL_PROVIDER):
    async with httpx.AsyncClient(timeout=10) as client:
        data = {
            "code": code,
            "client_id": integrationsettings.GOOGLE_CLIENT_ID,
            "client_secret": integrationsettings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": integrationsettings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        response = await client.post(GOOGLE_TOKEN_ENDPOINT, data=data)
        response.raise_for_status()

        token_data = response.json()

        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in", 3600)  # Default to 1 hour if missing
        
        if provider == DRIVE_PROVIDER:
            default_scopes = integrationsettings.GOOGLE_DRIVE_SCOPES
        elif provider == SHEETS_PROVIDER:
            default_scopes = integrationsettings.GOOGLE_SHEETS_SCOPES
        else:
            default_scopes = integrationsettings.GOOGLE_GMAIL_SCOPES
            
        granted_scopes = token_data.get("scope", default_scopes)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        return access_token, refresh_token, expires_at , granted_scopes


# ============================
# REFRESH ACCESS TOKEN
# ============================

async def refresh_google_access_token(refresh_token: str):
    async with httpx.AsyncClient(timeout=10) as client:
        data = {
            "refresh_token": refresh_token,
            "client_id": integrationsettings.GOOGLE_CLIENT_ID,
            "client_secret": integrationsettings.GOOGLE_CLIENT_SECRET,
            "grant_type": "refresh_token",
        }

        try:
            resp = await client.post(GOOGLE_TOKEN_ENDPOINT, data=data)
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            # OAuth error (invalid_grant, etc.) - return None so caller can remove token
            try:
                err = resp.json()
            except Exception:
                err = {"error": "http_status_error", "status_code": resp.status_code}
            # optional: log err for debug
            return None, None
        except Exception:
            # network / timeout etc.
            return None, None

        js = resp.json()
        new_access_token = js.get("access_token")
        expires_in = js.get("expires_in", 3600)

        if not new_access_token:
            return None, None

        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        return new_access_token, expires_at

# ============================
# ENSURE VALID TOKEN (AUTO REFRESH)
# ============================

async def ensure_valid_token(session: AsyncSession, user_id: UUID, provider: str = GMAIL_PROVIDER):
    token = await get_token(session, user_id, provider)
    if not token:
        return None

    now = datetime.now(timezone.utc)

    # If we don't have an expiry recorded, assume token is valid for research experiments.
    if not token.expires_at:
        return token

    # If still valid, return
    if token.expires_at > now:
        return token

    # expired -> attempt refresh only if we have a refresh_token
    if not token.refresh_token:
        # can't refresh, delete token (or return None)
        await delete_token(session, user_id, provider)
        return None

    new_access, new_expiry = await refresh_google_access_token(token.refresh_token)

    if not new_access:
        # refresh token invalid → delete token
        await delete_token(session, user_id, provider)
        return None

    # save updated access token (keep same refresh token/scopes)
    updated = await create_or_update_token(
        session=session,
        user_id=user_id,
        provider=provider,
        access_token=new_access,
        refresh_token=token.refresh_token,
        scopes=token.scopes,
        expires_at=new_expiry
    )

    return updated


# ============================
# CONNECT USER AFTER CALLBACK
# ============================

async def connect_user_google(
    session: AsyncSession,
    user_id: UUID,
    code: str,
    provider: str = GMAIL_PROVIDER
):
    access_token, refresh_token, expires_at, granted_scopes = await exchange_code_for_tokens(code, provider)

    token = await create_or_update_token(
        session=session,
        user_id=user_id,
        provider=provider,
        access_token=access_token,
        refresh_token=refresh_token,
        scopes=granted_scopes,
        expires_at=expires_at
    )

    return token


# ============================
# DISCONNECT USER (WITH GOOGLE REVOCATION)
# ============================

async def disconnect_user_google(
    session: AsyncSession,
    user_id: UUID,
    provider: str = GMAIL_PROVIDER
):
    """
    1. Fetches the stored token.
    2. Sends a revocation request to Google so the token is invalidated on their side.
    3. Deletes the token from our database.
    """
    token = await get_token(session, user_id, provider)
    
    if not token:
        return False

    # Revoke tokens on Google side
    # We prefer revoking the refresh_token as it kills the entire grant, 
    # but we'll try access_token as a fallback.
    token_to_revoke = token.refresh_token or token.access_token
    
    if token_to_revoke:
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                # Google revoke endpoint takes the token as a query parameter or POST body
                params = {"token": token_to_revoke}
                resp = await client.post(GOOGLE_REVOKE_ENDPOINT, params=params)
                # We don't necessarily want to block disconnection if revoke fails 
                # (e.g. if token already expired), but we logged it in a real scenario.
                if resp.status_code != 200:
                    print(f"Warning: Google token revocation returned status {resp.status_code}")
            except Exception as e:
                print(f"Error revoking Google token: {str(e)}")

    # Always clean up our database
    return await delete_token(session, user_id, provider)


# 7. AGENT VALIDATOR (NEW FUNCTION)
async def validate_google_capability(
    session: AsyncSession, 
    user_id: UUID, 
    required_scope_substring: str,
    provider: str = GMAIL_PROVIDER
) -> Dict:
    """
    Called by the AI Agent.
    Checks if connected AND if the specific permission (e.g. 'gmail.send') exists.
    """
    
    # A. Check connection & refresh if needed
    token_entry = await ensure_valid_token(session, user_id, provider)
    
    if not token_entry:
        # If we had a token but it failed to refresh, ensure_valid_token already deleted it.
        # We should tell the user to RE-connect if they used to be connected.
        return {
            "authorized": False, 
            "error": f"Your Google {provider.split('_')[1].capitalize()} connection has expired or been revoked. Please go to Settings and 'Connect' your account again."
        }

    # B. Check Permissions
    user_scopes = token_entry.scopes or ""
    
    if required_scope_substring not in user_scopes:
        return {
            "authorized": False, 
            "error": f"Your Google {provider.split('_')[1].capitalize()} connection is missing the '{required_scope_substring}' permission. Please disconnect and reconnect to grant all required permissions."
        }

    # C. Success
    return {
        "authorized": True, 
        "access_token": token_entry.access_token
    }
