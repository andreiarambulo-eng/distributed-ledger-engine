from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "backend-service"
    environment: str = "local"
    debug: bool = False

    # Databases & Caches
    postgres_dsn: str = "postgresql://app:app@localhost:5432/app"
    redis_url: str = "redis://localhost:6379/0"
    mongo_dsn: str = "mongodb://localhost:27017"
    mongo_db_name: str = "app"
    es_url: str = "http://localhost:9200"

    # Security & Rate Limiting
    upstream_api_key: str = ""
    rate_limit_rpm: int = 60


settings = Settings()
