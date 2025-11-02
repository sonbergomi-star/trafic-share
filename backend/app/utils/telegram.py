"""Telegram auth utilities."""

import hashlib
import hmac
from typing import Dict

from app.core.config import settings


def verify_telegram_auth(data: Dict[str, str | int]) -> bool:
    """Verify Telegram login widget signature."""

    received_hash = data.get("hash")
    if not received_hash:
        return False

    secret_key = hashlib.sha256(settings.telegram_bot_token.encode()).digest()
    check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(data.items()) if k != "hash" and v is not None
    )
    calculated_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(calculated_hash, str(received_hash))
