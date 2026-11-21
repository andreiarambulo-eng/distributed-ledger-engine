import pytest_asyncio
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings, settings
from app.domain.entities import ServiceHealth
from app.domain.protocols import HealthCheckRepository
from app.main import create_app
from app.services.health import HealthService


class MockHealthRepository:
    async def check_postgres(self) -> ServiceHealth:
        return ServiceHealth(name="postgres", status="healthy", latency_ms=1.2)

    async def check_redis(self) -> ServiceHealth:
        return ServiceHealth(name="redis", status="healthy", latency_ms=0.5)


class TestProvider(Provider):
    @provide(scope=Scope.APP)
    def get_settings(self) -> Settings:
        return settings

    @provide(scope=Scope.REQUEST)
    def get_health_repo(self) -> HealthCheckRepository:
        return MockHealthRepository()

    @provide(scope=Scope.REQUEST)
    def get_health_service(
        self, cfg: Settings, repo: HealthCheckRepository
    ) -> HealthService:
        return HealthService(settings=cfg, health_repo=repo)


@pytest_asyncio.fixture
async def client():
    """Async HTTP test client with mocked infrastructure dependencies."""
    container = make_async_container(TestProvider(), FastapiProvider())
    test_app = create_app()
    setup_dishka(container, test_app)

    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as ac:
        yield ac

    await container.close()
