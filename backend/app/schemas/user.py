from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    phone_number: Optional[str] = None


class UserUpdate(BaseModel):
    """User update schema"""
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None


class UserResponse(UserBase):
    """User response schema"""
    id: int
    balance_usd: float
    sent_mb: float
    used_mb: float
    is_active: bool
    is_banned: bool
    created_at: datetime
    last_seen: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    """User profile response with additional details"""
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    balance_usd: float
    sent_mb: float
    used_mb: float
    total_sessions: int
    total_earned: float
    created_at: datetime
    last_seen: Optional[datetime]
