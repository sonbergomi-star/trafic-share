"""Transaction endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.models import Transaction
from app.schemas import TransactionListResponse


router = APIRouter()


@router.get("/transactions", response_model=TransactionListResponse)
async def list_transactions(
    limit: int = 20,
    offset: int = 0,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    stmt = (
        select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .order_by(Transaction.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    rows = (await session.execute(stmt)).scalars().all()
    return TransactionListResponse(
        items=[
            {
                "id": tx.id,
                "type": tx.type.value,
                "amount_usd": float(tx.amount_usd),
                "status": tx.status.value,
                "created_at": tx.created_at,
                "note": tx.note,
            }
            for tx in rows
        ],
        total=len(rows),
    )
