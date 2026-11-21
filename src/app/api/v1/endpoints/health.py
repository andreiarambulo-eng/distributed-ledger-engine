from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Response, status

from app.api.schemas import ServiceHealthResponse, SystemHealthResponse
from app.services.health import HealthService

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "/liveness",
    response_model=SystemHealthResponse,
    summary="Liveness Probe",
    description="Returns alive status if the application process is running.",
)
@inject
async def get_liveness(
    service: FromDishka[HealthService],
) -> SystemHealthResponse:
    health = service.get_liveness()
    return SystemHealthResponse(
        app_name=health.app_name,
        environment=health.environment,
        status=health.status,
        timestamp=health.timestamp,
        services=[],
    )


@router.get(
    "/readiness",
    response_model=SystemHealthResponse,
    summary="Readiness Probe",
    description="Validates connections to database and cache backends.",
)
@inject
async def get_readiness(
    response: Response,
    service: FromDishka[HealthService],
) -> SystemHealthResponse:
    health = await service.get_readiness()

    if health.status != "healthy":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return SystemHealthResponse(
        app_name=health.app_name,
        environment=health.environment,
        status=health.status,
        timestamp=health.timestamp,
        services=[
            ServiceHealthResponse(
                name=s.name,
                status=s.status,
                latency_ms=s.latency_ms,
                details=s.details,
            )
            for s in health.services
        ],
    )
