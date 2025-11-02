from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TransactionBase(BaseModel):
    """Base transaction schema"""
    type: str
    amount_usd: float
    description: Optional[str] = None


class TransactionCreate(TransactionBase):
    """Transaction creation schema"""
    telegram_id: int


class TransactionResponse(TransactionBase):
    """Transaction response schema"""
    id: int
    telegram_id: int
    status: str
    note: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class WithdrawRequest(BaseModel):
    """Withdraw request schema"""
    amount_usd: float = Field(..., gt=0, description="Amount in USD")
    wallet_address: str = Field(..., min_length=10, description="USDT BEP20 wallet address")
    network: str = Field(default="BEP20", description="Network (BEP20)")


class WithdrawResponse(BaseModel):
    """Withdraw response schema"""
    id: int
    telegram_id: int
    amount_usd: float
    amount_usdt: float
    wallet_address: str
    network: str
    status: str
    payout_id: Optional[str]
    tx_hash: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True
