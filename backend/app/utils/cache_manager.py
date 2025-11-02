from typing import Optional, Any
import json
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)


class CacheManager:
    """Cache management utility (Redis-based)"""
    
    def __init__(self, redis_client=None):
        self.redis = redis_client
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis:
            return None
        
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL"""
        if not self.redis:
            return False
        
        try:
            serialized = json.dumps(value)
            self.redis.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.redis:
            return False
        
        try:
            self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.redis:
            return False
        
        try:
            return self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment value in cache"""
        if not self.redis:
            return None
        
        try:
            return self.redis.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error: {e}")
            return None
    
    def expire(self, key: str, ttl: int) -> bool:
        """Set expiry time for key"""
        if not self.redis:
            return False
        
        try:
            self.redis.expire(key, ttl)
            return True
        except Exception as e:
            logger.error(f"Cache expire error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.redis:
            return 0
        
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return 0
    
    # Helper methods for specific cache operations
    
    def cache_user_balance(self, telegram_id: int, balance: float, ttl: int = 60):
        """Cache user balance"""
        key = f"user:balance:{telegram_id}"
        return self.set(key, balance, ttl)
    
    def get_cached_user_balance(self, telegram_id: int) -> Optional[float]:
        """Get cached user balance"""
        key = f"user:balance:{telegram_id}"
        return self.get(key)
    
    def cache_session_data(self, session_id: str, data: dict, ttl: int = 300):
        """Cache session data"""
        key = f"session:{session_id}"
        return self.set(key, data, ttl)
    
    def get_cached_session_data(self, session_id: str) -> Optional[dict]:
        """Get cached session data"""
        key = f"session:{session_id}"
        return self.get(key)
    
    def cache_daily_price(self, date_str: str, price_data: dict, ttl: int = 3600):
        """Cache daily price"""
        key = f"price:daily:{date_str}"
        return self.set(key, price_data, ttl)
    
    def get_cached_daily_price(self, date_str: str) -> Optional[dict]:
        """Get cached daily price"""
        key = f"price:daily:{date_str}"
        return self.get(key)
    
    def cache_ip_reputation(self, ip: str, reputation_data: dict, ttl: int = 86400):
        """Cache IP reputation data"""
        key = f"ip:reputation:{ip}"
        return self.set(key, reputation_data, ttl)
    
    def get_cached_ip_reputation(self, ip: str) -> Optional[dict]:
        """Get cached IP reputation"""
        key = f"ip:reputation:{ip}"
        return self.get(key)
    
    def rate_limit_check(self, identifier: str, max_requests: int, window_seconds: int) -> tuple[bool, int]:
        """Check rate limit"""
        key = f"ratelimit:{identifier}"
        
        try:
            current = self.redis.get(key)
            if current is None:
                self.redis.setex(key, window_seconds, 1)
                return True, max_requests - 1
            
            current_count = int(current)
            if current_count >= max_requests:
                ttl = self.redis.ttl(key)
                return False, 0
            
            self.redis.incr(key)
            remaining = max_requests - (current_count + 1)
            return True, remaining
        
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return True, max_requests
    
    def lock(self, lock_key: str, ttl: int = 30) -> bool:
        """Acquire distributed lock"""
        if not self.redis:
            return False
        
        try:
            return self.redis.setnx(f"lock:{lock_key}", "1") and self.redis.expire(f"lock:{lock_key}", ttl)
        except Exception as e:
            logger.error(f"Lock acquire error: {e}")
            return False
    
    def unlock(self, lock_key: str) -> bool:
        """Release distributed lock"""
        return self.delete(f"lock:{lock_key}")
