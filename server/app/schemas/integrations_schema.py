from pydantic import BaseModel
from typing import Dict


class IntegrationStatus(BaseModel):
    provider: str
    connected: bool


class IntegrationStatusResponse(BaseModel):
    status: Dict[str, IntegrationStatus]


class ConnectURLResponse(BaseModel):
    auth_url: str


class OAuthSuccess(BaseModel):
    provider: str
    status: str = "connected"


class DisconnectResponse(BaseModel):
    provider: str
    status: str = "disconnected"
