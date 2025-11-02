"""Security helpers for JWT tokens and hashing."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(subject: str, additional_claims: Dict[str, Any] | None = None) -> str:
    """Generate a signed JWT access token."""

    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_access_token_ttl_minutes)).timestamp()),
    }
    if additional_claims:
        payload.update(additional_claims)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str, additional_claims: Dict[str, Any] | None = None) -> str:
    """Generate a signed JWT refresh token."""

    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_refresh_token_ttl_minutes)).timestamp()),
        "type": "refresh",
    }
    if additional_claims:
        payload.update(additional_claims)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token."""

    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a stored hash."""

    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash a password for storage."""

    return pwd_context.hash(password)
