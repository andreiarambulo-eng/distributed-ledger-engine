from collections.abc import AsyncIterable
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import FastapiProvider
from elasticsearch import AsyncElasticsearch
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool
from redis.asyncio import Redis

from app.core.config import Settings, settings
from app.domain.protocols import HealthCheckRepository
from app.infrastructure.repositories import PostgresRedisHealthRepository
from app.services.health import HealthService


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    def get_settings(self) -> Settings:
        return settings

    # 1. PostgreSQL: Singleton Pool (APP) -> Borrowed Connection (REQUEST)
    @provide(scope=Scope.APP)
    async def get_pg_pool(self, cfg: Settings) -> AsyncIterable[AsyncConnectionPool]:
        pool = AsyncConnectionPool(conninfo=cfg.postgres_dsn, min_size=2, max_size=10, open=False)
        await pool.open()
        yield pool
        await pool.close()

    @provide(scope=Scope.REQUEST)
    async def get_pg_conn(self, pool: AsyncConnectionPool) -> AsyncIterable[AsyncConnection]:
        async with pool.connection() as conn:
            yield conn

    # 2. Redis: Singleton Client (Built-in Pool)
    @provide(scope=Scope.APP)
    async def get_redis(self, cfg: Settings) -> AsyncIterable[Redis]:
        client = Redis.from_url(cfg.redis_url, decode_responses=True)
        yield client
        await client.aclose()

    # 3. MongoDB: Singleton Client & Database Handle (Built-in Pool)
    @provide(scope=Scope.APP)
    async def get_mongo_client(self, cfg: Settings) -> AsyncIterable[AsyncIOMotorClient]:
        client = AsyncIOMotorClient(cfg.mongo_dsn)
        yield client
        client.close()

    @provide(scope=Scope.APP)
    def get_mongo_db(self, client: AsyncIOMotorClient, cfg: Settings) -> AsyncIOMotorDatabase:
        return client[cfg.mongo_db_name]

    # 4. Elasticsearch: Singleton Async Client (Built-in Pool)
    @provide(scope=Scope.APP)
    async def get_es(self, cfg: Settings) -> AsyncIterable[AsyncElasticsearch]:
        client = AsyncElasticsearch(hosts=[cfg.es_url])
        yield client
        await client.close()


class AppProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_health_repo(self, conn: AsyncConnection, redis: Redis) -> HealthCheckRepository:
        return PostgresRedisHealthRepository(pg_conn=conn, redis=redis)

    @provide(scope=Scope.REQUEST)
    def get_health_service(
        self, cfg: Settings, repo: HealthCheckRepository
    ) -> HealthService:
        return HealthService(settings=cfg, health_repo=repo)


def create_container(*extra_providers: Provider):
    """Create and configure the root Dishka async container."""
    return make_async_container(
        *extra_providers,
        DatabaseProvider(),
        AppProvider(),
        FastapiProvider(),
    )
