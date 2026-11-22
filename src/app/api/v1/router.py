from fastapi import APIRouter, Depends

from app.api.schemas import ErrorResponse
from app.api.security import require_api_key
from app.api.v1.endpoints import auth, health

api_v1_router = APIRouter(prefix="/api/v1")

# Public: health probes must work without credentials (load balancers, Kubernetes).
api_v1_router.include_router(health.router)

# Protected: every router included here requires a valid X-API-Key.
protected_router = APIRouter(
    dependencies=[Depends(require_api_key)],
    responses={401: {"model": ErrorResponse, "description": "Invalid or missing API key"}},
)
protected_router.include_router(auth.router)

api_v1_router.include_router(protected_router)
