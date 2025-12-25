from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.core.deps import get_current_user

from app.schemas.integrations_schema import (
    IntegrationStatus,
    IntegrationStatusResponse
)

from app.db.crud.crud_integrations import is_connected
from app.services.integrations.google import PROVIDER_NAME as GOOGLE_PROVIDER

router = APIRouter(prefix="/integrations", tags=["Integrations - Status"])


@router.get("/status", response_model=IntegrationStatusResponse)
async def get_integration_status(
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user)
):
    status_dict = {
        GOOGLE_PROVIDER: IntegrationStatus(
            provider=GOOGLE_PROVIDER,
            connected=await is_connected(session, user.id, GOOGLE_PROVIDER)
        )
    }

    return IntegrationStatusResponse(status=status_dict)
