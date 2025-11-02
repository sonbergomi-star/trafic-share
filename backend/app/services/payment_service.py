from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from typing import Dict, Any
import logging
import httpx

from app.models.user import User
from app.models.transaction import Transaction, WithdrawRequest
from app.core.config import settings
from app.utils.validators import Validators

logger = logging.getLogger(__name__)


class PaymentService:
    """REAL Payment processing service for USDT BEP20 withdrawals"""
    
    MIN_WITHDRAW = 1.39
    MAX_WITHDRAW = 100.00
    WITHDRAW_FEE = 0.0
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_withdraw_request(
        self,
        telegram_id: int,
        amount_usd: float,
        wallet_address: str,
        network: str = "BEP20"
    ) -> Dict[str, Any]:
        """
        REAL withdraw request creation with validation
        """
        # Validate amount
        if amount_usd < self.MIN_WITHDRAW:
            raise ValueError(f"Minimum withdraw amount is ${self.MIN_WITHDRAW}")
        
        if amount_usd > self.MAX_WITHDRAW:
            raise ValueError(f"Maximum withdraw amount is ${self.MAX_WITHDRAW}")
        
        # Validate wallet address
        if not Validators.validate_wallet_address(wallet_address, network):
            raise ValueError("Invalid wallet address format")
        
        # Get user
        user_result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        # Check pending withdrawals
        pending_result = await self.db.execute(
            select(func.sum(WithdrawRequest.amount_usd))
            .where(WithdrawRequest.telegram_id == telegram_id)
            .where(WithdrawRequest.status.in_(['pending', 'processing']))
        )
        pending_amount = pending_result.scalar() or 0.0
        
        # Check available balance
        available_balance = user.balance_usd - pending_amount
        
        if available_balance < amount_usd:
            raise ValueError(f"Insufficient balance. Available: ${available_balance:.2f}")
        
        # Calculate USDT amount (1:1 for simplicity)
        amount_usdt = amount_usd
        
        # Create withdraw request
        withdraw = WithdrawRequest(
            telegram_id=telegram_id,
            amount_usd=amount_usd,
            amount_usdt=amount_usdt,
            wallet_address=wallet_address,
            network=network,
            status='pending',
            reserved_balance=True,
            created_at=datetime.utcnow()
        )
        
        self.db.add(withdraw)
        await self.db.commit()
        await self.db.refresh(withdraw)
        
        logger.info(
            f"Withdraw request created: ID={withdraw.id} "
            f"user={telegram_id} amount=${amount_usd}"
        )
        
        return {
            "withdraw_id": withdraw.id,
            "amount_usd": float(amount_usd),
            "amount_usdt": float(amount_usdt),
            "wallet_address": wallet_address,
            "network": network,
            "status": "pending",
            "created_at": withdraw.created_at.isoformat(),
        }
    
    async def process_withdraw(self, withdraw_id: int) -> Dict[str, Any]:
        """
        REAL withdraw processing (sends to payment provider)
        """
        # Get withdraw request
        result = await self.db.execute(
            select(WithdrawRequest).where(WithdrawRequest.id == withdraw_id)
        )
        withdraw = result.scalar_one_or_none()
        
        if not withdraw:
            raise ValueError("Withdraw request not found")
        
        if withdraw.status != 'pending':
            raise ValueError(f"Withdraw is already {withdraw.status}")
        
        # Update status to processing
        withdraw.status = 'processing'
        await self.db.commit()
        
        try:
            # Send to payment provider (NowPayments, Coinbase, etc.)
            payout_result = await self._send_payout(
                amount=withdraw.amount_usdt,
                wallet_address=withdraw.wallet_address,
                network=withdraw.network
            )
            
            if payout_result['success']:
                # Mark as completed
                withdraw.status = 'completed'
                withdraw.payout_id = payout_result.get('payout_id')
                withdraw.tx_hash = payout_result.get('tx_hash')
                withdraw.processed_at = datetime.utcnow()
                
                # Deduct from user balance
                user_result = await self.db.execute(
                    select(User).where(User.telegram_id == withdraw.telegram_id)
                )
                user = user_result.scalar_one()
                user.balance_usd -= withdraw.amount_usd
                
                # Create transaction record
                transaction = Transaction(
                    telegram_id=withdraw.telegram_id,
                    type='withdraw',
                    amount_usd=-withdraw.amount_usd,  # Negative for withdrawal
                    status='completed',
                    description=f"USDT withdrawal to {withdraw.wallet_address[:10]}...",
                    created_at=datetime.utcnow()
                )
                self.db.add(transaction)
                
                await self.db.commit()
                
                logger.info(
                    f"Withdraw completed: ID={withdraw_id} "
                    f"tx_hash={payout_result.get('tx_hash')}"
                )
                
                return {
                    "status": "completed",
                    "withdraw_id": withdraw_id,
                    "tx_hash": withdraw.tx_hash,
                    "payout_id": withdraw.payout_id,
                }
            else:
                # Mark as failed
                withdraw.status = 'failed'
                withdraw.error_message = payout_result.get('error')
                await self.db.commit()
                
                logger.error(f"Withdraw failed: ID={withdraw_id} error={payout_result.get('error')}")
                
                return {
                    "status": "failed",
                    "withdraw_id": withdraw_id,
                    "error": payout_result.get('error')
                }
        
        except Exception as e:
            # Mark as failed
            withdraw.status = 'failed'
            withdraw.error_message = str(e)
            await self.db.commit()
            
            logger.error(f"Withdraw processing error: ID={withdraw_id} error={e}")
            
            raise
    
    async def _send_payout(
        self,
        amount: float,
        wallet_address: str,
        network: str
    ) -> Dict[str, Any]:
        """
        Send payout to payment provider API
        In production, integrate with NowPayments, Coinbase Commerce, or similar
        """
        # MOCK implementation for development
        # In production, replace with actual API calls
        
        if settings.DEBUG:
            # Mock successful payout for development
            import uuid
            return {
                "success": True,
                "payout_id": f"PAY_{uuid.uuid4().hex[:16].upper()}",
                "tx_hash": f"0x{uuid.uuid4().hex}",
            }
        
        # Real implementation example (NowPayments)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.nowpayments.io/v1/payout",
                    headers={
                        "x-api-key": settings.PAYMENT_PROVIDER_API_KEY,
                        "Content-Type": "application/json"
                    },
                    json={
                        "withdrawals": [{
                            "address": wallet_address,
                            "currency": "usdtbep20",
                            "amount": amount,
                            "ipn_callback_url": f"https://{settings.VPS_IP}/api/withdraw/webhook"
                        }]
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "payout_id": data.get('id'),
                        "tx_hash": data.get('hash'),
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Payment provider error: {response.status_code}"
                    }
        
        except Exception as e:
            logger.error(f"Payment provider API error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_withdraw_status(self, withdraw_id: int) -> Dict[str, Any]:
        """
        REAL get withdraw request status
        """
        result = await self.db.execute(
            select(WithdrawRequest).where(WithdrawRequest.id == withdraw_id)
        )
        withdraw = result.scalar_one_or_none()
        
        if not withdraw:
            raise ValueError("Withdraw request not found")
        
        return {
            "withdraw_id": withdraw.id,
            "amount_usd": float(withdraw.amount_usd),
            "amount_usdt": float(withdraw.amount_usdt),
            "wallet_address": withdraw.wallet_address,
            "network": withdraw.network,
            "status": withdraw.status,
            "payout_id": withdraw.payout_id,
            "tx_hash": withdraw.tx_hash,
            "error_message": withdraw.error_message,
            "created_at": withdraw.created_at.isoformat(),
            "processed_at": withdraw.processed_at.isoformat() if withdraw.processed_at else None,
        }
    
    async def get_withdraw_history(
        self,
        telegram_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        REAL withdraw history from database
        """
        # Get total count
        count_result = await self.db.execute(
            select(func.count(WithdrawRequest.id))
            .where(WithdrawRequest.telegram_id == telegram_id)
        )
        total = count_result.scalar()
        
        # Get withdrawals
        result = await self.db.execute(
            select(WithdrawRequest)
            .where(WithdrawRequest.telegram_id == telegram_id)
            .order_by(WithdrawRequest.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        withdrawals = result.scalars().all()
        
        return {
            "withdrawals": [
                {
                    "id": w.id,
                    "amount_usd": float(w.amount_usd),
                    "amount_usdt": float(w.amount_usdt),
                    "wallet_address": w.wallet_address,
                    "network": w.network,
                    "status": w.status,
                    "tx_hash": w.tx_hash,
                    "created_at": w.created_at.isoformat(),
                    "processed_at": w.processed_at.isoformat() if w.processed_at else None,
                }
                for w in withdrawals
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    
    async def cancel_withdraw(
        self,
        withdraw_id: int,
        telegram_id: int
    ) -> Dict[str, Any]:
        """
        REAL cancel pending withdraw request
        """
        result = await self.db.execute(
            select(WithdrawRequest)
            .where(WithdrawRequest.id == withdraw_id)
            .where(WithdrawRequest.telegram_id == telegram_id)
        )
        withdraw = result.scalar_one_or_none()
        
        if not withdraw:
            raise ValueError("Withdraw request not found")
        
        if withdraw.status not in ['pending', 'processing']:
            raise ValueError(f"Cannot cancel withdraw with status: {withdraw.status}")
        
        # Cancel withdraw
        withdraw.status = 'cancelled'
        withdraw.reserved_balance = False
        await self.db.commit()
        
        logger.info(f"Withdraw cancelled: ID={withdraw_id} by user {telegram_id}")
        
        return {
            "status": "cancelled",
            "withdraw_id": withdraw_id,
            "amount_returned": float(withdraw.amount_usd)
        }
