import base64
import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt

from app.core.config import get_settings


settings = get_settings()


def _get_telegram_secret_key(bot_token: str) -> bytes:
    return hashlib.sha256(bot_token.encode()).digest()


def verify_telegram_signature(auth_data: Dict[str, Any]) -> bool:
    """Validate Telegram login widget auth payload signature."""

    if "hash" not in auth_data:
        return False

    check_hash = auth_data["hash"]
    data_check_arr = []
    for key in sorted(k for k in auth_data.keys() if k != "hash"):
        value = auth_data[key]
        if isinstance(value, (dict, list)):
            continue
        data_check_arr.append(f"{key}={value}")

    data_check_string = "\n".join(data_check_arr)
    secret_key = _get_telegram_secret_key(settings.telegram_bot_token)
    hmac_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(hmac_hash, check_hash)


def create_access_token(payload: Dict[str, Any], expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.jwt_access_ttl_minutes))
    to_encode = {**payload, "exp": expire}
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


def mask_token(token: str, visible: int = 6) -> str:
    if not token:
        return ""
    if len(token) <= visible * 2:
        return token
    return f"{token[:visible]}...{token[-visible:]}"


def generate_idempotency_key(namespace: str, seed: str) -> str:
    raw = f"{namespace}:{seed}".encode()
    return base64.urlsafe_b64encode(hashlib.sha256(raw).digest()).decode().rstrip("=")

