"""Balance schemas."""

from datetime import datetime

from pydantic import BaseModel


class BalanceResponse(BaseModel):
    user: dict
    balance: dict
    today_earn: float
    month_earn: float
    transactions: list[dict]


class BalanceRefreshRequest(BaseModel):
    telegram_id: int


class BalanceRefreshResponse(BaseModel):
    status: str
    new_balance_usd: float
    delta: float
    refreshed_at: datetime
