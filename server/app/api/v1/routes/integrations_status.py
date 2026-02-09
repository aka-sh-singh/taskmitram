from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.core.deps import get_current_user

from app.schemas.integrations_schema import (
    IntegrationStatus,
    IntegrationStatusResponse
)

from app.services.integration_service import get_all_integration_statuses_service

router = APIRouter(prefix="/integrations", tags=["Integrations - Status"])


@router.get("/status", response_model=IntegrationStatusResponse)
async def get_integration_status(
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user)
):
    return await get_all_integration_statuses_service(session, user.id)
