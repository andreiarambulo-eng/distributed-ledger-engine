import os
from typing import Annotated, Any

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

LOCAL_ENVIRONMENT = "local"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # APP_ENV_FILE lets tests load .env.test; real environment variables always win.
        env_file=os.getenv("APP_ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "backend-service"
    environment: str = LOCAL_ENVIRONMENT
    debug: bool = False

    # Databases & Caches
    postgres_dsn: str = "postgresql://app:app@localhost:5432/app"
    redis_url: str = "redis://localhost:6379/0"
    mongo_dsn: str = "mongodb://localhost:27017"
    mongo_db_name: str = "app"
    es_url: str = "http://localhost:9200"

    # Security
    # Comma-separated in the environment: API_KEYS=key-a,key-b (several keys allow rotation).
    api_keys: Annotated[list[SecretStr], NoDecode] = Field(default_factory=list)

    @field_validator("api_keys", mode="before")
    @classmethod
    def _split_api_keys(cls, value: Any) -> Any:
        if isinstance(value, str):
            value = value.split(",")
        if isinstance(value, list):
            return [key.strip() for key in value if isinstance(key, str) and key.strip()]
        return value

    @model_validator(mode="after")
    def _require_api_keys_outside_local(self) -> "Settings":
        if self.environment != LOCAL_ENVIRONMENT and not self.api_keys:
            raise ValueError(
                f"API_KEYS must be set when ENVIRONMENT is not '{LOCAL_ENVIRONMENT}' "
                f"(got ENVIRONMENT='{self.environment}')."
            )
        return self


settings = Settings()
