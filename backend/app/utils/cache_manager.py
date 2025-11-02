from typing import Optional, Dict, Any
import json
import redis.asyncio as redis
from datetime import timedelta
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """
    REAL Redis cache manager
    Handles IP reputation caching and session data
    """
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis = redis_client
        self._connected = False
    
    async def connect(self):
        """REAL connect to Redis"""
        if not self.redis:
            try:
                self.redis = await redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True
                )
                self._connected = True
                logger.info("Redis connected")
            except Exception as e:
                logger.error(f"Redis connection failed: {e}")
                self._connected = False
    
    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            self._connected = False
    
    def get_cached_ip_reputation(self, ip: str) -> Optional[Dict[str, Any]]:
        """
        REAL get cached IP reputation data
        """
        if not self._connected or not self.redis:
            return None
        
        try:
            key = f"ip_reputation:{ip}"
            cached = self.redis.get(key)
            
            if cached:
                return json.loads(cached)
            
            return None
        
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def cache_ip_reputation(
        self,
        ip: str,
        data: Dict[str, Any],
        ttl: int = 86400
    ):
        """
        REAL cache IP reputation data
        TTL in seconds (default 24h)
        """
        if not self._connected or not self.redis:
            return
        
        try:
            key = f"ip_reputation:{ip}"
            value = json.dumps(data)
            
            self.redis.setex(
                key,
                timedelta(seconds=ttl),
                value
            )
            
            logger.debug(f"Cached IP reputation for {ip}")
        
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    async def cache_session_data(
        self,
        session_id: str,
        data: Dict[str, Any],
        ttl: int = 3600
    ):
        """
        REAL cache session temporary data
        """
        if not self._connected or not self.redis:
            return
        
        try:
            key = f"session:{session_id}"
            value = json.dumps(data)
            
            await self.redis.setex(
                key,
                timedelta(seconds=ttl),
                value
            )
        
        except Exception as e:
            logger.error(f"Cache session error: {e}")
    
    async def get_cached_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get cached session data"""
        if not self._connected or not self.redis:
            return None
        
        try:
            key = f"session:{session_id}"
            cached = await self.redis.get(key)
            
            if cached:
                return json.loads(cached)
            
            return None
        
        except Exception as e:
            logger.error(f"Get cached session error: {e}")
            return None
