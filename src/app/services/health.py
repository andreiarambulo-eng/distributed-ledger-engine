from datetime import datetime, timezone

from app.core.config import Settings
from app.domain.entities import ServiceHealth, SystemHealth
from app.domain.protocols import HealthCheckRepository


class HealthService:
    """Application service for orchestrating liveness and readiness health checks."""

    def __init__(self, settings: Settings, health_repo: HealthCheckRepository) -> None:
        self._settings = settings
        self._repo = health_repo

    def get_liveness(self) -> SystemHealth:
        """Lightweight check to verify the process is alive."""
        return SystemHealth(
            app_name=self._settings.app_name,
            environment=self._settings.environment,
            status="alive",
            timestamp=datetime.now(timezone.utc),
            services=[],
        )

    async def get_readiness(self) -> SystemHealth:
        """Readiness check verifying connectivity to critical infrastructure."""
        services: list[ServiceHealth] = []

        pg_health = await self._repo.check_postgres()
        services.append(pg_health)

        redis_health = await self._repo.check_redis()
        services.append(redis_health)

        overall_status = "healthy"
        if any(s.status == "unhealthy" for s in services):
            overall_status = "degraded"

        return SystemHealth(
            app_name=self._settings.app_name,
            environment=self._settings.environment,
            status=overall_status,
            timestamp=datetime.now(timezone.utc),
            services=services,
        )
