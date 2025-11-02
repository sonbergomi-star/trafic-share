"""Redis cache helpers."""

import asyncio
from typing import AsyncIterator

import redis.asyncio as aioredis

from app.core.config import settings


redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """Return a shared Redis connection."""

    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(settings.redis_url)
    return redis_client


async def redis_dependency() -> AsyncIterator[aioredis.Redis]:
    """FastAPI dependency for redis connection."""

    client = await get_redis()
    try:
        yield client
    finally:
        # pooled client, no close
        await asyncio.sleep(0)
