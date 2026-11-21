import time
from psycopg import AsyncConnection
from redis.asyncio import Redis

from app.domain.entities import ServiceHealth
from app.domain.protocols import HealthCheckRepository


class PostgresRedisHealthRepository(HealthCheckRepository):
    """Concrete implementation of HealthCheckRepository using psycopg and redis-py."""

    def __init__(self, pg_conn: AsyncConnection, redis: Redis) -> None:
        self._pg_conn = pg_conn
        self._redis = redis

    async def check_postgres(self) -> ServiceHealth:
        start = time.perf_counter()
        try:
            async with self._pg_conn.cursor() as cur:
                await cur.execute("SELECT 1;")
                await cur.fetchone()
            latency = (time.perf_counter() - start) * 1000
            return ServiceHealth(name="postgres", status="healthy", latency_ms=round(latency, 2))
        except Exception as exc:
            latency = (time.perf_counter() - start) * 1000
            return ServiceHealth(
                name="postgres",
                status="unhealthy",
                latency_ms=round(latency, 2),
                details=str(exc),
            )

    async def check_redis(self) -> ServiceHealth:
        start = time.perf_counter()
        try:
            await self._redis.ping()
            latency = (time.perf_counter() - start) * 1000
            return ServiceHealth(name="redis", status="healthy", latency_ms=round(latency, 2))
        except Exception as exc:
            latency = (time.perf_counter() - start) * 1000
            return ServiceHealth(
                name="redis",
                status="unhealthy",
                latency_ms=round(latency, 2),
                details=str(exc),
            )
