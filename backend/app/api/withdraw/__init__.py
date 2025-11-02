from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.transaction import WithdrawRequest, Transaction


router = APIRouter()


class WithdrawCreateRequest(BaseModel):
    telegram_id: int
    amount_usd: float
    wallet_address: str
    network: str = "BEP20"


class WithdrawResponse(BaseModel):
    status: str
    withdraw_id: int
    message: str


@router.post("", response_model=WithdrawResponse)
async def create_withdraw(request: WithdrawCreateRequest, db: AsyncSession = Depends(get_db)):
    """
    Create withdraw request
    """
    # Validate amount
    if request.amount_usd < settings.MIN_WITHDRAW_USD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Minimum withdraw amount is ${settings.MIN_WITHDRAW_USD}"
        )
    
    if request.amount_usd > settings.MAX_WITHDRAW_USD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum withdraw amount is ${settings.MAX_WITHDRAW_USD}"
        )
    
    # Get user
    result = await db.execute(
        select(User).where(User.telegram_id == request.telegram_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check balance
    if user.balance_usd < request.amount_usd:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance"
        )
    
    # Validate wallet address (basic BEP20 validation)
    if not request.wallet_address.startswith("0x") or len(request.wallet_address) != 42:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid BEP20 wallet address"
        )
    
    # Create withdraw request
    idempotency_key = str(uuid.uuid4())
    withdraw = WithdrawRequest(
        telegram_id=request.telegram_id,
        amount_usd=request.amount_usd,
        amount_usdt=request.amount_usd * 0.9,  # Approximate conversion
        wallet_address=request.wallet_address,
        network=request.network,
        idempotency_key=idempotency_key,
        status="pending",
        reserved_balance=True,
    )
    
    # Reserve balance
    user.balance_usd -= request.amount_usd
    
    db.add(withdraw)
    await db.commit()
    await db.refresh(withdraw)
    
    return {
        "status": "pending",
        "withdraw_id": withdraw.id,
        "message": "Withdraw request created and queued for processing"
    }


@router.get("/history/{telegram_id}")
async def get_withdraw_history(telegram_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get withdraw history for user
    """
    result = await db.execute(
        select(WithdrawRequest)
        .where(WithdrawRequest.telegram_id == telegram_id)
        .order_by(WithdrawRequest.created_at.desc())
        .limit(10)
    )
    withdraws = result.scalars().all()
    
    return {
        "withdraws": [
            {
                "id": w.id,
                "amount_usd": w.amount_usd,
                "amount_usdt": w.amount_usdt,
                "wallet_address": w.wallet_address,
                "status": w.status,
                "tx_hash": w.tx_hash,
                "created_at": w.created_at.isoformat(),
                "processed_at": w.processed_at.isoformat() if w.processed_at else None,
            }
            for w in withdraws
        ]
    }
