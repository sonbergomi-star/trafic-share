from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.dependencies import get_current_user
from app.models.withdraw import WithdrawRequest, WithdrawStatus
from app.core.config import settings
import uuid
import re

router = APIRouter()


class WithdrawRequestModel(BaseModel):
    amount_usd: float
    wallet_address: str
    network: str = "BEP20"
    idempotency_key: str = None


@router.post("")
async def create_withdraw(
    request: WithdrawRequestModel,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create withdraw request"""
    # Validate amount
    if request.amount_usd < settings.MIN_WITHDRAW_USD:
        raise HTTPException(status_code=400, detail=f"Minimum withdraw is ${settings.MIN_WITHDRAW_USD}")
    
    if request.amount_usd > settings.MAX_WITHDRAW_USD:
        raise HTTPException(status_code=400, detail=f"Maximum withdraw is ${settings.MAX_WITHDRAW_USD}")
    
    # Check balance
    if float(current_user.balance_usd) < request.amount_usd:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Validate wallet address
    if request.network == "BEP20":
        if not re.match(r'^0x[a-fA-F0-9]{40}$', request.wallet_address):
            raise HTTPException(status_code=400, detail="Invalid BEP20 address format")
    
    # Check idempotency
    idempotency_key = request.idempotency_key or str(uuid.uuid4())
    existing = db.query(WithdrawRequest).filter(
        WithdrawRequest.idempotency_key == idempotency_key
    ).first()
    
    if existing:
        return {
            "status": existing.status.value,
            "withdraw_id": existing.id,
            "message": "Request already exists"
        }
    
    # Calculate USDT amount
    amount_usdt = request.amount_usd * settings.DEFAULT_USD_TO_USDT_RATE
    
    # Reserve balance
    from app.services.user_service import update_user_balance
    update_user_balance(db, current_user.telegram_id, -request.amount_usd, "Withdraw reservation")
    
    # Create withdraw request
    withdraw_req = WithdrawRequest(
        telegram_id=current_user.telegram_id,
        amount_usd=request.amount_usd,
        amount_usdt=amount_usdt,
        wallet_address=request.wallet_address,
        network=request.network,
        status=WithdrawStatus.PENDING,
        idempotency_key=idempotency_key,
        reserved_balance=True
    )
    
    db.add(withdraw_req)
    db.commit()
    db.refresh(withdraw_req)
    
    # TODO: Queue payout worker
    
    return {
        "status": "pending",
        "withdraw_id": withdraw_req.id,
        "message": "Withdraw request queued and will be processed shortly"
    }


@router.get("")
async def get_withdraws(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's withdraw history"""
    withdraws = db.query(WithdrawRequest).filter(
        WithdrawRequest.telegram_id == current_user.telegram_id
    ).order_by(WithdrawRequest.created_at.desc()).limit(5).all()
    
    return [
        {
            "id": w.id,
            "amount_usd": float(w.amount_usd),
            "wallet_address": w.wallet_address,
            "status": w.status.value,
            "tx_hash": w.tx_hash,
            "created_at": w.created_at.isoformat() if w.created_at else None,
        }
        for w in withdraws
    ]
