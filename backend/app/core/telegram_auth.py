import hashlib
import hmac
from typing import Dict, Optional
from app.core.config import settings


def verify_telegram_auth(auth_data: Dict) -> bool:
    """
    Verify Telegram authentication data using bot token
    """
    if not settings.TELEGRAM_BOT_TOKEN:
        return False
    
    # Extract hash from auth_data
    received_hash = auth_data.get("hash")
    if not received_hash:
        return False
    
    # Create secret key from bot token
    secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
    
    # Remove hash from data for verification
    data_check = auth_data.copy()
    data_check.pop("hash", None)
    
    # Sort data by key and create data_check_string
    data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(data_check.items())])
    
    # Calculate hash
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return calculated_hash == received_hash


def parse_telegram_auth_data(auth_data: Dict) -> Optional[Dict]:
    """Parse and validate Telegram auth data"""
    if not verify_telegram_auth(auth_data):
        return None
    
    return {
        "telegram_id": int(auth_data.get("id", 0)),
        "username": auth_data.get("username", ""),
        "first_name": auth_data.get("first_name", ""),
        "photo_url": auth_data.get("photo_url", ""),
        "auth_date": int(auth_data.get("auth_date", 0)),
    }
