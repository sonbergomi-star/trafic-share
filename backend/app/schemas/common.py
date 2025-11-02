from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List
from datetime import datetime


T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    """Generic response model"""
    status: str = "success"
    message: Optional[str] = None
    data: Optional[T] = None
    timestamp: datetime = datetime.utcnow()


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model"""
    items: List[T]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool


class ErrorResponse(BaseModel):
    """Error response model"""
    status: str = "error"
    error_code: str
    message: str
    details: Optional[dict] = None
    timestamp: datetime = datetime.utcnow()


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime
    database: str
    redis: str
