from functools import lru_cache
from typing import Any, List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    app_name: str = Field(default="Traffic Sharing Platform")
    environment: str = Field(default="development")
    debug: bool = Field(default=True)

    database_url: str = Field(..., alias="DATABASE_URL")
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")

    telegram_bot_username: str = Field(..., alias="TELEGRAM_BOT_USERNAME")
    telegram_bot_token: str = Field(..., alias="TELEGRAM_BOT_TOKEN")

    jwt_secret: str = Field(..., alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_ttl_minutes: int = Field(default=60 * 24 * 7)  # 7 days

    fcm_server_key: Optional[str] = Field(default=None, alias="FCM_SERVER_KEY")

    admin_ids: List[int] = Field(default_factory=list, alias="ADMIN_IDS")
    allowed_origins: List[str] = Field(default_factory=lambda: ["*"], alias="ALLOWED_ORIGINS")

    default_price_per_gb: float = Field(default=1.50)
    min_withdraw_usd: float = Field(default=1.39)
    max_withdraw_usd: float = Field(default=100.0)

    price_poll_interval_minutes: int = Field(default=5)
    notification_batch_size: int = Field(default=1000)

    project_domain: Optional[str] = Field(default=None, alias="PROJECT_DOMAIN")

    def parse_admin_ids(self, value: Any) -> List[int]:
        if isinstance(value, list):
            return [int(v) for v in value]
        if isinstance(value, str) and value.strip():
            return [int(v.strip()) for v in value.split(",") if v.strip()]
        return []

    def parse_allowed_origins(self, value: Any) -> List[str]:
        if isinstance(value, list):
            return value
        if isinstance(value, str) and value.strip():
            return [v.strip() for v in value.split(",") if v.strip()]
        return ["*"]

    @property
    def admin_id_set(self) -> set[int]:
        return set(self.admin_ids)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.admin_ids = settings.parse_admin_ids(settings.admin_ids)
    settings.allowed_origins = settings.parse_allowed_origins(settings.allowed_origins)
    return settings

