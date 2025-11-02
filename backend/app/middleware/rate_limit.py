from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # Store: {ip: [(timestamp, count_minute, count_hour), ...]}
        self.request_history: Dict[str, list] = {}
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limit
        if not self._check_rate_limit(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Record request
        self._record_request(client_ip)
        
        # Continue with request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining_minute, remaining_hour = self._get_remaining(client_ip)
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(remaining_minute)
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Hour"] = str(remaining_hour)
        
        return response
    
    def _check_rate_limit(self, ip: str) -> bool:
        """Check if IP is within rate limits"""
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        if ip not in self.request_history:
            return True
        
        # Clean old entries
        self.request_history[ip] = [
            timestamp for timestamp in self.request_history[ip]
            if timestamp > hour_ago
        ]
        
        # Count requests
        minute_count = sum(1 for t in self.request_history[ip] if t > minute_ago)
        hour_count = len(self.request_history[ip])
        
        return (
            minute_count < self.requests_per_minute and
            hour_count < self.requests_per_hour
        )
    
    def _record_request(self, ip: str):
        """Record a request from IP"""
        if ip not in self.request_history:
            self.request_history[ip] = []
        
        self.request_history[ip].append(datetime.utcnow())
    
    def _get_remaining(self, ip: str) -> Tuple[int, int]:
        """Get remaining requests for IP"""
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        if ip not in self.request_history:
            return self.requests_per_minute, self.requests_per_hour
        
        minute_count = sum(1 for t in self.request_history[ip] if t > minute_ago)
        hour_count = len(self.request_history[ip])
        
        return (
            max(0, self.requests_per_minute - minute_count),
            max(0, self.requests_per_hour - hour_count)
        )
