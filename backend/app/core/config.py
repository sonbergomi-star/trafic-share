"""Application configuration management."""

from functools import lru_cache
from typing import List, Optional

from pydantic import AnyHttpUrl, Field
from pydantic.functional_validators import field_validator
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    app_name: str = Field(default="Traffic Platform Backend")
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    secret_key: str = Field(default="change-me")
    jwt_secret: str = Field(default="change-me")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_ttl_minutes: int = Field(default=60 * 24)
    jwt_refresh_token_ttl_minutes: int = Field(default=60 * 24 * 7)

    telegram_bot_token: str = Field(default="")
    telegram_bot_username: str = Field(default="")
    telegram_admin_chat_id: Optional[str] = None

    database_url: str = Field(default="postgresql+asyncpg://postgres:postgres@db:5432/traffic")
    sync_database_url: str | None = Field(
        default=None,
        validation_alias="DATABASE_URL_SYNC",
    )

    redis_url: str = Field(default="redis://redis:6379/0")
    celery_broker_url: str = Field(default="redis://redis:6379/1")
    celery_result_backend: str = Field(default="redis://redis:6379/2")

    fcm_credentials_path: Optional[str] = None
    fcm_project_id: Optional[str] = None

    allowed_origins: List[AnyHttpUrl] = Field(default_factory=list)

    admin_ids: List[int] = Field(default_factory=list)

    pricing_cache_ttl_seconds: int = Field(default=60 * 60)
    ip_cache_ttl_seconds: int = Field(default=60 * 60 * 24)
    vpn_score_block_threshold: int = Field(default=70)
    vpn_score_warn_threshold: int = Field(default=50)
    allowed_regions: List[str] = Field(default_factory=lambda: ["US", "CA", "GB", "DE", "FR", "NL", "ES", "IT"])
    allowed_network_types: List[str] = Field(default_factory=lambda: ["mobile", "wifi"])
    max_start_attempts_per_day: int = Field(default=5)

    min_withdraw_usd: float = Field(default=1.39)
    max_withdraw_usd: float = Field(default=100.0)
    withdraw_rate_limit_per_minute: int = Field(default=1)
    daily_withdraw_limit: int = Field(default=3)

    default_usd_to_usdt_rate: float = Field(default=0.9)

    prometheus_metrics_enabled: bool = Field(default=True)

    class Config:
        arbitrary_types_allowed = True

    @field_validator("admin_ids", mode="before")
    @classmethod
    def _split_admin_ids(cls, value: List[int] | str | None) -> List[int]:
        if value is None or value == "":
            return []
        if isinstance(value, str):
            return [int(item.strip()) for item in value.split(",") if item.strip()]
        return value

    @model_validator(mode="after")
    def _populate_sync_url(self) -> "Settings":
        if not self.sync_database_url and "+asyncpg" in self.database_url:
            self.sync_database_url = self.database_url.replace("+asyncpg", "+psycopg")
        elif not self.sync_database_url:
            self.sync_database_url = self.database_url
        return self


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()


settings = get_settings()
