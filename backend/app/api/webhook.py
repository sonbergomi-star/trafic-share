from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import hmac
import hashlib
import logging
from datetime import datetime

from app.core.database import get_db
from app.core.config import settings
from app.models.withdraw_request import WithdrawRequest
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/payment/nowpayments")
async def nowpayments_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    REAL NowPayments webhook handler
    Receives payment status updates
    """
    # Verify webhook signature
    signature = request.headers.get('x-nowpayments-sig')
    
    if not signature:
        logger.warning("NowPayments webhook: missing signature")
        raise HTTPException(status_code=401, detail="Missing signature")
    
    # Get raw body
    body = await request.body()
    
    # Verify signature
    expected_sig = hmac.new(
        settings.PAYMENT_PROVIDER_API_KEY.encode(),
        body,
        hashlib.sha512
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_sig):
        logger.warning("NowPayments webhook: invalid signature")
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse webhook data
    try:
        data = await request.json()
    except Exception as e:
        logger.error(f"NowPayments webhook: invalid JSON: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Get payment data
    payout_id = data.get('id')
    status = data.get('status')  # sending, confirming, confirmed, failed
    tx_hash = data.get('hash')
    
    if not payout_id:
        logger.warning("NowPayments webhook: missing payout_id")
        raise HTTPException(status_code=400, detail="Missing payout_id")
    
    # Find withdraw request
    result = await db.execute(
        select(WithdrawRequest)
        .where(WithdrawRequest.payout_id == payout_id)
    )
    withdraw = result.scalar_one_or_none()
    
    if not withdraw:
        logger.warning(f"NowPayments webhook: withdraw not found for payout {payout_id}")
        raise HTTPException(status_code=404, detail="Withdraw not found")
    
    # Update withdraw status
    old_status = withdraw.status
    
    if status == 'confirmed':
        withdraw.status = 'completed'
        withdraw.tx_hash = tx_hash
        withdraw.processed_at = datetime.utcnow()
        
        logger.info(f"Withdraw {withdraw.id} completed: ${withdraw.amount_usd}")
        
        # Send notification
        try:
            from app.services.notification_service import NotificationService
            notif_service = NotificationService(db)
            await notif_service.send_withdraw_status(
                telegram_id=withdraw.telegram_id,
                withdraw_id=withdraw.id,
                status='completed',
                amount=float(withdraw.amount_usd),
                tx_hash=tx_hash
            )
        except Exception as e:
            logger.error(f"Failed to send withdraw notification: {e}")
    
    elif status == 'failed':
        withdraw.status = 'failed'
        withdraw.note = data.get('error', 'Payment failed')
        withdraw.processed_at = datetime.utcnow()
        
        # Refund balance if deducted
        if withdraw.reserved_balance:
            user_result = await db.execute(
                select(User).where(User.telegram_id == withdraw.telegram_id)
            )
            user = user_result.scalar_one_or_none()
            
            if user:
                user.balance_usd += withdraw.amount_usd
                logger.info(f"Refunded ${withdraw.amount_usd} to user {user.telegram_id}")
        
        # Send notification
        try:
            from app.services.notification_service import NotificationService
            notif_service = NotificationService(db)
            await notif_service.send_withdraw_status(
                telegram_id=withdraw.telegram_id,
                withdraw_id=withdraw.id,
                status='failed',
                amount=float(withdraw.amount_usd)
            )
        except Exception as e:
            logger.error(f"Failed to send withdraw notification: {e}")
    
    elif status in ['sending', 'confirming']:
        withdraw.status = 'processing'
    
    await db.commit()
    
    logger.info(
        f"Withdraw {withdraw.id} status updated: "
        f"{old_status} -> {withdraw.status}"
    )
    
    return {"status": "ok"}
