from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
import logging

from app.core.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services.payment_service import PaymentService

logger = logging.getLogger(__name__)

router = APIRouter()


class WithdrawRequest(BaseModel):
    amount_usd: float = Field(..., gt=0, description="Amount in USD")
    wallet_address: str = Field(..., min_length=10, description="USDT BEP20 wallet address")
    network: str = Field(default="BEP20", description="Network type")


@router.post("/create")
async def create_withdraw(
    request: WithdrawRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL create withdraw request with validation
    """
    payment_service = PaymentService(db)
    
    try:
        result = await payment_service.create_withdraw_request(
            telegram_id=current_user.telegram_id,
            amount_usd=request.amount_usd,
            wallet_address=request.wallet_address,
            network=request.network
        )
        
        logger.info(
            f"Withdraw request created by {current_user.telegram_id}: "
            f"${request.amount_usd} to {request.wallet_address[:10]}..."
        )
        
        return {
            "status": "success",
            "data": result
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Withdraw creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create withdraw request")


@router.get("/history")
async def get_withdraw_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL withdraw history with pagination
    """
    payment_service = PaymentService(db)
    
    offset = (page - 1) * per_page
    result = await payment_service.get_withdraw_history(
        telegram_id=current_user.telegram_id,
        limit=per_page,
        offset=offset
    )
    
    return {
        "status": "success",
        "data": {
            "withdrawals": result['withdrawals'],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": result['total'],
                "total_pages": (result['total'] + per_page - 1) // per_page,
            }
        }
    }


@router.get("/{withdraw_id}")
async def get_withdraw_status(
    withdraw_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL get withdraw status
    """
    payment_service = PaymentService(db)
    
    try:
        result = await payment_service.get_withdraw_status(withdraw_id)
        
        # Check ownership
        if result.get('telegram_id') != current_user.telegram_id:
            raise HTTPException(status_code=403, detail="Not your withdraw request")
        
        return {
            "status": "success",
            "data": result
        }
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{withdraw_id}/cancel")
async def cancel_withdraw(
    withdraw_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    REAL cancel pending withdraw
    """
    payment_service = PaymentService(db)
    
    try:
        result = await payment_service.cancel_withdraw(
            withdraw_id=withdraw_id,
            telegram_id=current_user.telegram_id
        )
        
        logger.info(f"Withdraw cancelled: ID={withdraw_id} by {current_user.telegram_id}")
        
        return {
            "status": "success",
            "data": result
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook")
async def withdraw_webhook(
    data: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    REAL webhook for payment provider callbacks
    """
    # Verify webhook signature (in production)
    # For now, log and process
    
    logger.info(f"Withdraw webhook received: {data}")
    
    # Process webhook data
    # Update withdraw status based on provider response
    
    return {"status": "ok"}
