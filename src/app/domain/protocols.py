from typing import Protocol
from app.domain.entities import ServiceHealth


class HealthCheckRepository(Protocol):
    """Protocol for checking the operational readiness of persistent backends."""

    async def check_postgres(self) -> ServiceHealth:
        ...

    async def check_redis(self) -> ServiceHealth:
        ...
