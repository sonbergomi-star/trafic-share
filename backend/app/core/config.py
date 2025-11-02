from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Traffic Sharing Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    # Database
    DATABASE_URL: str
    
    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 10080  # 7 days
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_BOT_USERNAME: str
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Admin
    ADMIN_IDS: str = ""
    
    # Payment
    PAYMENT_PROVIDER_API_KEY: str = ""
    PAYMENT_PROVIDER_API_SECRET: str = ""
    PAYMENT_PROVIDER_CALLBACK_URL: str = ""
    MIN_WITHDRAW_USD: float = 1.39
    MAX_WITHDRAW_USD: float = 100.00
    
    # FCM
    FCM_SERVER_KEY: str = ""
    FCM_PROJECT_ID: str = ""
    
    # Traffic
    TRAFFIC_POOL_SERVERS: str = ""
    
    # VPS
    VPS_IP: str = "113.30.191.89"
    VPS_USERNAME: str = "adminuser"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def admin_ids_list(self) -> List[int]:
        if not self.ADMIN_IDS:
            return []
        return [int(id.strip()) for id in self.ADMIN_IDS.split(",") if id.strip()]


settings = Settings()
