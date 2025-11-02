"""Withdraw schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class WithdrawRequestCreate(BaseModel):
    telegram_id: int
    amount_usd: float
    wallet_address: str
    network: str = "BEP20"
    idempotency_key: Optional[str] = None


class WithdrawResponse(BaseModel):
    status: str
    transaction_id: int
    message: str


class WithdrawItem(BaseModel):
    id: int
    amount_usd: float
    status: str
    created_at: datetime
    processed_at: Optional[datetime]
    tx_hash: Optional[str]


class WithdrawListResponse(BaseModel):
    items: list[WithdrawItem]
    total: int
