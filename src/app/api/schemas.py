from datetime import datetime
from pydantic import BaseModel, Field


class ServiceHealthResponse(BaseModel):
    name: str
    status: str
    latency_ms: float | None = None
    details: str | None = None


class SystemHealthResponse(BaseModel):
    app_name: str
    environment: str
    status: str
    timestamp: datetime
    services: list[ServiceHealthResponse] = Field(default_factory=list)


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
