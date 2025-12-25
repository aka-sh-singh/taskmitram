# app/db/crud/crud_integrations.py
from datetime import datetime, timezone
from uuid import UUID
from typing import Optional, List, Set, Union
import json

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.db.models.integration_token import IntegrationToken


# -----------------------
# Scope normalization
# -----------------------
def normalize_scopes(scopes: Optional[Union[str, List[str]]]) -> Optional[str]:
    """
    Normalize scopes into a stable JSON array string for storage.
    Accepts:
      - None -> None
      - space/comma separated string -> JSON list
      - list[str] -> JSON list
    Returns JSON string or None.
    """
    if not scopes:
        return None
    if isinstance(scopes, str):
        parts = [s.strip() for s in scopes.replace(",", " ").split() if s.strip()]
        unique = sorted(set(parts))
        return json.dumps(unique)
    if isinstance(scopes, list):
        unique = sorted(set([s.strip() for s in scopes if s and s.strip()]))
        return json.dumps(unique)
    return None


def parse_scopes_field(scopes_field: Optional[str]) -> Set[str]:
    """
    Parse the stored scopes field (JSON list or fallback string) and return a set.
    """
    if not scopes_field:
        return set()
    try:
        val = json.loads(scopes_field)
        if isinstance(val, list):
            return set(s for s in val if isinstance(s, str))
    except Exception:
        # fallback to whitespace/comma split
        return set(s.strip() for s in scopes_field.replace(",", " ").split() if s.strip())
    return set()


# -------------------------------------------------------------
# Get token for specific provider (Google Gmail, Notion, etc.)
# -------------------------------------------------------------
async def get_token(
    session: AsyncSession,
    user_id: UUID,
    provider: str
) -> Optional[IntegrationToken]:

    query = select(IntegrationToken).where(
        (IntegrationToken.user_id == user_id) &
        (IntegrationToken.provider == provider)
    )

    result = await session.execute(query)
    return result.scalars().first()


# -------------------------------------------------------------
# Get all tokens for a user (used for /integrations/status)
# -------------------------------------------------------------
async def get_all_tokens_for_user(
    session: AsyncSession,
    user_id: UUID
) -> List[IntegrationToken]:

    query = select(IntegrationToken).where(
        IntegrationToken.user_id == user_id
    )

    result = await session.execute(query)
    return result.scalars().all()


# -------------------------------------------------------------
# Create or Update an Integration Token (concurrency-safe upsert)
# Used in Google OAuth callback
# -------------------------------------------------------------
async def create_or_update_token(
    session: AsyncSession,
    user_id: UUID,
    provider: str,
    access_token: str,
    refresh_token: Optional[str],
    scopes: Optional[Union[str, List[str]]],
    expires_at
) -> IntegrationToken:
    """
    Upsert the IntegrationToken for (user_id, provider).
    Scopes are normalized to a JSON array string before saving.
    Uses simple IntegrityError retry to handle rare race conditions.
    """
    normalized = normalize_scopes(scopes)

    existing = await get_token(session, user_id, provider)

    if existing:
        existing.access_token = access_token
        existing.refresh_token = refresh_token
        existing.scopes = normalized
        existing.expires_at = expires_at
        existing.updated_at = datetime.now(timezone.utc)
        session.add(existing)
        await session.commit()
        await session.refresh(existing)
        return existing

    new_token = IntegrationToken(
        user_id=user_id,
        provider=provider,
        access_token=access_token,
        refresh_token=refresh_token,
        scopes=normalized,
        expires_at=expires_at
    )
    session.add(new_token)
    try:
        await session.commit()
    except IntegrityError:
        # Concurrent insert happened: rollback and fetch existing, then update it
        await session.rollback()
        existing = await get_token(session, user_id, provider)
        if existing:
            existing.access_token = access_token
            existing.refresh_token = refresh_token
            existing.scopes = normalized
            existing.expires_at = expires_at
            existing.updated_at = datetime.now(timezone.utc)
            session.add(existing)
            await session.commit()
            await session.refresh(existing)
            return existing
        # If still no existing token, re-raise
        raise
    await session.refresh(new_token)
    return new_token


# -------------------------------------------------------------
# Delete token for a provider (disconnect)
# -------------------------------------------------------------
async def delete_token(
    session: AsyncSession,
    user_id: UUID,
    provider: str
) -> bool:

    token = await get_token(session, user_id, provider)

    if token:
        await session.delete(token)
        await session.commit()
        return True

    return False


# -------------------------------------------------------------
# Convenience checks
# -------------------------------------------------------------
async def is_connected(session: AsyncSession, user_id: UUID, provider: str) -> bool:
    token = await get_token(session, user_id, provider)
    return token is not None


async def token_has_scopes(session: AsyncSession, user_id: UUID, provider: str, required_scopes: List[str]) -> bool:
    """
    Return True if the stored IntegrationToken for (user_id, provider)
    contains all required_scopes. Uses parse_scopes_field to handle storage formats.
    """
    tok = await get_token(session, user_id, provider)
    if not tok:
        return False
    have = parse_scopes_field(tok.scopes)
    return set(required_scopes).issubset(have)