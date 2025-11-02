"""Withdraw endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.core.cache import redis_dependency
from app.schemas import WithdrawListResponse, WithdrawRequestCreate, WithdrawResponse
from app.services.withdraw_service import WithdrawService


router = APIRouter()


@router.post("/withdraw", response_model=WithdrawResponse)
async def create_withdraw(
    payload: WithdrawRequestCreate,
    session: AsyncSession = Depends(get_db_session),
    redis=Depends(redis_dependency),
    current_user=Depends(get_current_user),
):
    service = WithdrawService(session, redis)
    withdraw = await service.create_withdraw(current_user, payload)
    return WithdrawResponse(
        status=withdraw.status.value,
        transaction_id=withdraw.id,
        message="Withdraw request queued and will be processed shortly.",
    )


@router.get("/withdraws", response_model=WithdrawListResponse)
async def list_withdraws(
    session: AsyncSession = Depends(get_db_session),
    redis=Depends(redis_dependency),
    current_user=Depends(get_current_user),
):
    service = WithdrawService(session, redis)
    rows = await service.list_withdraws(current_user)
    return WithdrawListResponse(
        items=[
            {
                "id": item.id,
                "amount_usd": float(item.amount_usd),
                "status": item.status.value,
                "created_at": item.created_at,
                "processed_at": item.processed_at,
                "tx_hash": item.tx_hash,
            }
            for item in rows
        ],
        total=len(rows),
    )
