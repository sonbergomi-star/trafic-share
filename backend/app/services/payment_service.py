from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
import uuid
import logging

from app.models.user import User
from app.models.transaction import Transaction, WithdrawRequest
from app.core.config import settings

logger = logging.getLogger(__name__)


class PaymentService:
    """Payment processing service for withdrawals"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.provider_api_key = settings.PAYMENT_PROVIDER_API_KEY
        self.provider_api_secret = settings.PAYMENT_PROVIDER_API_SECRET
    
    async def create_withdraw_request(
        self,
        telegram_id: int,
        amount_usd: float,
        wallet_address: str,
        network: str = "BEP20"
    ) -> Dict[str, Any]:
        """Create a new withdraw request"""
        
        # Validate amount
        if amount_usd < settings.MIN_WITHDRAW_USD:
            raise ValueError(f"Minimum withdraw is ${settings.MIN_WITHDRAW_USD}")
        
        if amount_usd > settings.MAX_WITHDRAW_USD:
            raise ValueError(f"Maximum withdraw is ${settings.MAX_WITHDRAW_USD}")
        
        # Get user
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        # Check balance
        if user.balance_usd < amount_usd:
            raise ValueError("Insufficient balance")
        
        # Validate wallet address
        if not self._validate_wallet_address(wallet_address, network):
            raise ValueError("Invalid wallet address")
        
        # Generate idempotency key
        idempotency_key = str(uuid.uuid4())
        
        # Calculate USDT amount (approximate conversion)
        amount_usdt = amount_usd * 0.9  # Simplified conversion
        
        # Create withdraw request
        withdraw = WithdrawRequest(
            telegram_id=telegram_id,
            amount_usd=amount_usd,
            amount_usdt=amount_usdt,
            wallet_address=wallet_address,
            network=network,
            idempotency_key=idempotency_key,
            status="pending",
            reserved_balance=True,
        )
        
        # Reserve balance
        user.balance_usd -= amount_usd
        
        self.db.add(withdraw)
        
        # Create transaction record
        transaction = Transaction(
            telegram_id=telegram_id,
            type="withdraw",
            amount_usd=-amount_usd,
            amount_usdt=amount_usdt,
            currency="USDT",
            status="pending",
            description=f"Withdraw to {wallet_address[:10]}..."
        )
        self.db.add(transaction)
        
        await self.db.commit()
        await self.db.refresh(withdraw)
        
        return {
            "status": "pending",
            "withdraw_id": withdraw.id,
            "message": "Withdraw request created and queued for processing"
        }
    
    async def process_withdraw(self, withdraw_id: int) -> Dict[str, Any]:
        """Process a pending withdraw request"""
        
        result = await self.db.execute(
            select(WithdrawRequest).where(WithdrawRequest.id == withdraw_id)
        )
        withdraw = result.scalar_one_or_none()
        
        if not withdraw:
            raise ValueError("Withdraw request not found")
        
        if withdraw.status != "pending":
            return {
                "status": "error",
                "message": f"Withdraw is already {withdraw.status}"
            }
        
        # Update status to processing
        withdraw.status = "processing"
        await self.db.commit()
        
        # Send payout via provider
        try:
            payout_result = await self._send_payout(
                amount_usdt=withdraw.amount_usdt,
                wallet_address=withdraw.wallet_address,
                network=withdraw.network,
                idempotency_key=withdraw.idempotency_key
            )
            
            if payout_result["success"]:
                withdraw.payout_id = payout_result["payout_id"]
                withdraw.status = "completed"
                withdraw.processed_at = datetime.utcnow()
                withdraw.tx_hash = payout_result.get("tx_hash")
                withdraw.provider_response = payout_result
                
                # Update transaction
                transaction_result = await self.db.execute(
                    select(Transaction)
                    .where(Transaction.telegram_id == withdraw.telegram_id)
                    .where(Transaction.type == "withdraw")
                    .where(Transaction.amount_usd == -withdraw.amount_usd)
                    .order_by(Transaction.created_at.desc())
                )
                transaction = transaction_result.scalar_one_or_none()
                if transaction:
                    transaction.status = "completed"
                
                await self.db.commit()
                
                return {
                    "status": "completed",
                    "message": "Withdraw completed successfully",
                    "tx_hash": payout_result.get("tx_hash")
                }
            else:
                # Payout failed
                withdraw.status = "failed"
                withdraw.note = payout_result.get("error", "Unknown error")
                withdraw.provider_response = payout_result
                
                # Refund balance
                user_result = await self.db.execute(
                    select(User).where(User.telegram_id == withdraw.telegram_id)
                )
                user = user_result.scalar_one_or_none()
                if user:
                    user.balance_usd += withdraw.amount_usd
                
                await self.db.commit()
                
                return {
                    "status": "failed",
                    "message": payout_result.get("error", "Payout failed")
                }
        
        except Exception as e:
            logger.error(f"Error processing withdraw {withdraw_id}: {e}")
            withdraw.status = "failed"
            withdraw.note = str(e)
            await self.db.commit()
            
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _send_payout(
        self,
        amount_usdt: float,
        wallet_address: str,
        network: str,
        idempotency_key: str
    ) -> Dict[str, Any]:
        """Send payout via payment provider (mock implementation)"""
        
        # This is a mock implementation
        # In production, integrate with real payment provider (NowPayments, etc.)
        
        if not self.provider_api_key:
            logger.warning("Payment provider not configured - using mock")
            return {
                "success": True,
                "payout_id": f"MOCK_{idempotency_key[:8]}",
                "tx_hash": f"0x{uuid.uuid4().hex}",
                "message": "Mock payout (no real provider configured)"
            }
        
        # Example: NowPayments API integration
        url = "https://api.nowpayments.io/v1/payout"
        headers = {
            "x-api-key": self.provider_api_key,
            "Content-Type": "application/json",
        }
        
        payload = {
            "withdrawals": [
                {
                    "address": wallet_address,
                    "currency": "usdtbsc",  # USDT on BSC (BEP20)
                    "amount": amount_usdt,
                    "ipn_callback_url": settings.PAYMENT_PROVIDER_CALLBACK_URL,
                    "unique_external_id": idempotency_key,
                }
            ]
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "payout_id": data.get("id"),
                        "tx_hash": data.get("hash"),
                        "response": data
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Provider error: {response.status_code} - {response.text}"
                    }
        
        except Exception as e:
            logger.error(f"Payout request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _validate_wallet_address(self, address: str, network: str) -> bool:
        """Validate wallet address format"""
        
        if network == "BEP20":
            # BEP20 addresses are Ethereum-compatible
            if not address.startswith("0x"):
                return False
            if len(address) != 42:
                return False
            # Check if hex
            try:
                int(address[2:], 16)
                return True
            except ValueError:
                return False
        
        return False
    
    async def get_withdraw_status(self, withdraw_id: int) -> Dict[str, Any]:
        """Get withdraw request status"""
        
        result = await self.db.execute(
            select(WithdrawRequest).where(WithdrawRequest.id == withdraw_id)
        )
        withdraw = result.scalar_one_or_none()
        
        if not withdraw:
            raise ValueError("Withdraw request not found")
        
        return {
            "id": withdraw.id,
            "amount_usd": withdraw.amount_usd,
            "amount_usdt": withdraw.amount_usdt,
            "wallet_address": withdraw.wallet_address,
            "status": withdraw.status,
            "payout_id": withdraw.payout_id,
            "tx_hash": withdraw.tx_hash,
            "created_at": withdraw.created_at.isoformat(),
            "processed_at": withdraw.processed_at.isoformat() if withdraw.processed_at else None,
        }
    
    async def webhook_handler(self, provider: str, data: Dict[str, Any]) -> bool:
        """Handle webhook from payment provider"""
        
        # Extract payout info from webhook
        payout_id = data.get("id") or data.get("payout_id")
        status = data.get("status")
        tx_hash = data.get("hash") or data.get("tx_hash")
        
        if not payout_id:
            logger.warning("Webhook missing payout_id")
            return False
        
        # Find withdraw request
        result = await self.db.execute(
            select(WithdrawRequest).where(WithdrawRequest.payout_id == payout_id)
        )
        withdraw = result.scalar_one_or_none()
        
        if not withdraw:
            logger.warning(f"Withdraw not found for payout_id: {payout_id}")
            return False
        
        # Update status based on webhook
        if status in ["finished", "completed", "confirmed"]:
            withdraw.status = "completed"
            withdraw.tx_hash = tx_hash
            withdraw.processed_at = datetime.utcnow()
        elif status in ["failed", "rejected"]:
            withdraw.status = "failed"
            # Refund user balance
            user_result = await self.db.execute(
                select(User).where(User.telegram_id == withdraw.telegram_id)
            )
            user = user_result.scalar_one_or_none()
            if user and withdraw.reserved_balance:
                user.balance_usd += withdraw.amount_usd
        
        await self.db.commit()
        
        return True
