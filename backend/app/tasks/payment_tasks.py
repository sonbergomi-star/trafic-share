from datetime import datetime
from sqlalchemy import select
import logging

from app.tasks.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.services.payment_service import PaymentService
from app.models.transaction import WithdrawRequest

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.payment_tasks.process_withdrawal")
def process_withdrawal(withdraw_id: int):
    """Process a single withdrawal request (async task)"""
    
    import asyncio
    
    async def _process():
        async with AsyncSessionLocal() as db:
            payment_service = PaymentService(db)
            result = await payment_service.process_withdraw(withdraw_id)
            logger.info(f"Processed withdrawal {withdraw_id}: {result}")
            return result
    
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_process())


@celery_app.task(name="app.tasks.payment_tasks.process_pending_withdrawals")
def process_pending_withdrawals():
    """Process all pending withdrawal requests"""
    
    import asyncio
    
    async def _process_all():
        async with AsyncSessionLocal() as db:
            # Get pending withdrawals
            result = await db.execute(
                select(WithdrawRequest)
                .where(WithdrawRequest.status == 'pending')
                .order_by(WithdrawRequest.created_at)
                .limit(10)  # Process 10 at a time
            )
            
            withdrawals = result.scalars().all()
            
            payment_service = PaymentService(db)
            processed_count = 0
            
            for withdrawal in withdrawals:
                try:
                    await payment_service.process_withdraw(withdrawal.id)
                    processed_count += 1
                except Exception as e:
                    logger.error(f"Failed to process withdrawal {withdrawal.id}: {e}")
            
            logger.info(f"Processed {processed_count} withdrawals")
            return {"processed": processed_count, "total": len(withdrawals)}
    
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_process_all())


@celery_app.task(name="app.tasks.payment_tasks.check_withdrawal_status")
def check_withdrawal_status(withdraw_id: int):
    """Check status of a withdrawal from payment provider"""
    
    import asyncio
    
    async def _check():
        async with AsyncSessionLocal() as db:
            payment_service = PaymentService(db)
            result = await payment_service.get_withdraw_status(withdraw_id)
            logger.info(f"Withdrawal {withdraw_id} status: {result}")
            return result
    
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_check())


@celery_app.task(name="app.tasks.payment_tasks.retry_failed_withdrawal")
def retry_failed_withdrawal(withdraw_id: int):
    """Retry a failed withdrawal"""
    
    import asyncio
    
    async def _retry():
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(WithdrawRequest).where(WithdrawRequest.id == withdraw_id)
            )
            withdrawal = result.scalar_one_or_none()
            
            if not withdrawal:
                logger.error(f"Withdrawal {withdraw_id} not found")
                return {"status": "error", "message": "Withdrawal not found"}
            
            if withdrawal.status != 'failed':
                logger.error(f"Withdrawal {withdraw_id} is not in failed state")
                return {"status": "error", "message": "Withdrawal is not failed"}
            
            # Reset to pending
            withdrawal.status = 'pending'
            withdrawal.error_message = None
            await db.commit()
            
            # Process again
            payment_service = PaymentService(db)
            result = await payment_service.process_withdraw(withdraw_id)
            
            logger.info(f"Retried withdrawal {withdraw_id}: {result}")
            return result
    
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_retry())


@celery_app.task(name="app.tasks.payment_tasks.send_payment_reminder")
def send_payment_reminder(telegram_id: int, balance: float):
    """Send reminder to withdraw available balance"""
    
    import asyncio
    
    async def _send_reminder():
        from app.services.telegram_service import TelegramService
        
        telegram_service = TelegramService()
        
        message = f"""
?? <b>Balansni yechish eslatmasi</b>

Sizning balansingiz: ${balance:.2f}

Minimal yechish summasi: $1.39

Balance sahifasidan USDT BEP20 ga yechishingiz mumkin!
"""
        
        await telegram_service.send_message(telegram_id, message)
        logger.info(f"Sent payment reminder to user {telegram_id}")
    
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_send_reminder())
