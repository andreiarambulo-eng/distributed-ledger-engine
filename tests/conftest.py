import os
from pathlib import Path

# Must run before any `app` import: Settings reads APP_ENV_FILE when the module loads.
# Absolute path so tests work no matter which directory pytest is started from.
os.environ["APP_ENV_FILE"] = str(Path(__file__).resolve().parent.parent / ".env.test")

import pytest_asyncio
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import FastapiProvider
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings, settings
from app.domain.entities import ServiceHealth
from app.domain.protocols import HealthCheckRepository
from app.main import create_app
from app.services.auth import ApiKeyAuthenticator
from app.services.health import HealthService

# Keys come from API_KEYS in .env.test. Two keys let tests prove zero-downtime rotation.
TEST_API_KEYS = tuple(key.get_secret_value() for key in settings.api_keys)
assert len(TEST_API_KEYS) >= 2, ".env.test must define at least two API_KEYS"


class MockHealthRepository:
    async def check_postgres(self) -> ServiceHealth:
        return ServiceHealth(name="postgres", status="healthy", latency_ms=1.2)

    async def check_redis(self) -> ServiceHealth:
        return ServiceHealth(name="redis", status="healthy", latency_ms=0.5)


class TestProvider(Provider):
    @provide(scope=Scope.APP)
    def get_settings(self) -> Settings:
        return settings

    @provide(scope=Scope.APP)
    def get_api_key_authenticator(self, cfg: Settings) -> ApiKeyAuthenticator:
        return ApiKeyAuthenticator(settings=cfg)

    @provide(scope=Scope.REQUEST)
    def get_health_repo(self) -> HealthCheckRepository:
        return MockHealthRepository()

    @provide(scope=Scope.REQUEST)
    def get_health_service(self, cfg: Settings, repo: HealthCheckRepository) -> HealthService:
        return HealthService(settings=cfg, health_repo=repo)


@pytest_asyncio.fixture
async def client():
    """Async HTTP test client with mocked infrastructure dependencies."""
    container = make_async_container(TestProvider(), FastapiProvider())
    test_app = create_app(container=container)

    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        yield ac

    await container.close()
