from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.base import ORMModel
from app.schemas.user import UserBasic


class TransactionSchema(ORMModel):
    id: int
    telegram_id: int
    type: str
    amount_usd: float
    amount_usdt: Optional[float]
    currency: str
    status: str
    wallet_address: Optional[str]
    provider_payout_id: Optional[str]
    tx_hash: Optional[str]
    note: Optional[str]
    created_at: datetime


class TransactionsResponse(ORMModel):
    items: List[TransactionSchema]
    total: int


class RefreshBalanceResponse(ORMModel):
    status: str
    new_balance_usd: float
    delta: float


class RefreshBalancePayload(BaseModel):
    telegram_id: int
    delta: float = 0.0


class BalanceOverview(ORMModel):
    user: UserBasic
    balance_usd: float
    sent_mb: float
    used_mb: float
    today_earn: float
    month_earn: float
    transactions: List[TransactionSchema]


class WithdrawPayload(BaseModel):
    telegram_id: int
    amount_usd: float
    wallet_address: str
    network: str = Field(default="BEP20")
    idempotency_key: Optional[str] = None


class WithdrawResponse(ORMModel):
    status: str
    transaction_id: Optional[int]
    withdraw_id: int
    message: str


class WithdrawDetail(ORMModel):
    id: int
    telegram_id: int
    amount_usd: float
    amount_usdt: Optional[float]
    wallet_address: str
    network: str
    status: str
    payout_id: Optional[str]
    tx_hash: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]


class WithdrawListResponse(ORMModel):
    items: List[WithdrawDetail]
    total: int

