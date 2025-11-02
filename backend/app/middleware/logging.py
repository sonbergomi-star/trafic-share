from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Logging middleware for all requests"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = str(int(time.time() * 1000))
        
        # Get request info
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        
        # Log request start
        logger.info(
            f"[{request_id}] {method} {path} - IP: {client_ip} - Started"
        )
        
        # Process request
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log request completion
            logger.info(
                f"[{request_id}] {method} {path} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.3f}s"
            )
            
            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{duration:.3f}"
            
            return response
        
        except Exception as e:
            # Log error
            duration = time.time() - start_time
            logger.error(
                f"[{request_id}] {method} {path} - "
                f"Error: {str(e)} - "
                f"Duration: {duration:.3f}s"
            )
            raise


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Detailed request logging middleware"""
    
    async def dispatch(self, request: Request, call_next):
        # Log detailed request info
        timestamp = datetime.utcnow().isoformat()
        
        log_data = {
            "timestamp": timestamp,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client": {
                "host": request.client.host if request.client else None,
                "port": request.client.port if request.client else None,
            },
            "headers": {
                "user-agent": request.headers.get("user-agent"),
                "content-type": request.headers.get("content-type"),
                "authorization": "***" if request.headers.get("authorization") else None,
            }
        }
        
        logger.debug(f"Request: {log_data}")
        
        # Process request
        response = await call_next(request)
        
        # Log response
        logger.debug(
            f"Response: Status {response.status_code} for "
            f"{request.method} {request.url.path}"
        )
        
        return response
