from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings - REAL configuration"""
    
    # App
    APP_NAME: str = "Traffic Platform API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # VPS
    VPS_IP: str = "113.30.191.89"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/traffic_platform"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    
    # JWT
    JWT_SECRET_KEY: str = "CHANGE_THIS_TO_RANDOM_SECRET_KEY_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_DAYS: int = 7
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_BOT_USERNAME: str = ""
    
    # Admin IDs
    ADMIN_IDS: str = ""
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Payment
    PAYMENT_PROVIDER_API_KEY: str = ""
    
    # FCM
    FCM_SERVER_KEY: str = ""
    FCM_CREDENTIALS_PATH: str = ""
    
    # CORS
    ALLOWED_ORIGINS: str = "*"
    
    # Traffic Pool API
    TRAFFIC_POOL_API_KEY: str = ""
    TRAFFIC_POOL_API_URL: str = ""
    
    # Pricing
    DEFAULT_PRICE_PER_GB: float = 1.50
    MIN_WITHDRAW_USD: float = 1.39
    MAX_WITHDRAW_USD: float = 100.00
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    @property
    def admin_ids_list(self) -> List[int]:
        """Parse admin IDs from comma-separated string"""
        if not self.ADMIN_IDS:
            return []
        try:
            return [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip()]
        except:
            return []
    
    @property
    def database_url_sync(self) -> str:
        """Sync database URL for Alembic"""
        return self.DATABASE_URL.replace("+asyncpg", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
