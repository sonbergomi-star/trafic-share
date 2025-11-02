from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/traffic_db")
    
    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_DAYS: int = int(os.getenv("JWT_EXPIRATION_DAYS", "7"))
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_BOT_USERNAME: str = os.getenv("TELEGRAM_BOT_USERNAME", "")
    ADMIN_IDS: str = os.getenv("ADMIN_IDS", "")
    
    # Firebase
    FCM_SERVER_KEY: str = os.getenv("FCM_SERVER_KEY", "")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Payment
    PAYMENT_PROVIDER: str = os.getenv("PAYMENT_PROVIDER", "nowpayments")
    NOWPAYMENTS_API_KEY: str = os.getenv("NOWPAYMENTS_API_KEY", "")
    NOWPAYMENTS_API_SECRET: str = os.getenv("NOWPAYMENTS_API_SECRET", "")
    MIN_WITHDRAW_USD: float = float(os.getenv("MIN_WITHDRAW_USD", "1.39"))
    MAX_WITHDRAW_USD: float = float(os.getenv("MAX_WITHDRAW_USD", "100.00"))
    DEFAULT_USD_TO_USDT_RATE: float = float(os.getenv("DEFAULT_USD_TO_USDT_RATE", "0.90"))
    
    # Server
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # IP Filtering
    VPN_SCORE_BLOCK_THRESHOLD: int = int(os.getenv("VPN_SCORE_BLOCK_THRESHOLD", "70"))
    VPN_SCORE_WARN_THRESHOLD: int = int(os.getenv("VPN_SCORE_WARN_THRESHOLD", "50"))
    ALLOWED_REGIONS: List[str] = os.getenv("ALLOWED_REGIONS", "US,GB,DE,FR").split(",")
    
    # GeoIP
    MAXMIND_LICENSE_KEY: str = os.getenv("MAXMIND_LICENSE_KEY", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


def get_admin_ids() -> List[int]:
    """Parse admin IDs from environment variable"""
    if not settings.ADMIN_IDS:
        return []
    return [int(uid.strip()) for uid in settings.ADMIN_IDS.split(",") if uid.strip()]
