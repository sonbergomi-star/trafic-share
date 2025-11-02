"""Transaction schemas."""

from datetime import datetime

from pydantic import BaseModel


class TransactionItem(BaseModel):
    id: int
    type: str
    amount_usd: float
    status: str
    created_at: datetime
    note: str | None


class TransactionListResponse(BaseModel):
    items: list[TransactionItem]
    total: int
