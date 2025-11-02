from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

from app.models.session import Session
from app.models.user import User
from app.models.transaction import Transaction
from app.services.pricing_service import PricingService

logger = logging.getLogger(__name__)


class ReconciliationService:
    """
    REAL session and balance reconciliation
    Compares client-reported vs server-calculated data
    """
    
    # Acceptable difference threshold (1% or 5 MB)
    TOLERANCE_PERCENT = 0.01
    TOLERANCE_MB = 5.0
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pricing_service = PricingService(db)
    
    async def run_full_reconciliation(self) -> Dict[str, Any]:
        """
        REAL full system reconciliation
        Checks all sessions and balances
        """
        logger.info("Starting full reconciliation...")
        
        results = {
            "sessions_checked": 0,
            "sessions_ok": 0,
            "sessions_mismatch": 0,
            "balances_corrected": 0,
            "errors": []
        }
        
        # Get all completed sessions in last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        result = await self.db.execute(
            select(Session)
            .where(Session.status == "completed")
            .where(Session.started_at >= thirty_days_ago)
        )
        sessions = result.scalars().all()
        
        results["sessions_checked"] = len(sessions)
        
        # Check each session
        for session in sessions:
            try:
                is_ok = await self._reconcile_session(session)
                
                if is_ok:
                    results["sessions_ok"] += 1
                else:
                    results["sessions_mismatch"] += 1
            
            except Exception as e:
                logger.error(f"Session {session.id} reconciliation error: {e}")
                results["errors"].append({
                    "session_id": session.id,
                    "error": str(e)
                })
        
        # Reconcile user balances
        balance_corrections = await self._reconcile_all_balances()
        results["balances_corrected"] = balance_corrections
        
        await self.db.commit()
        
        logger.info(
            f"Reconciliation complete: "
            f"checked={results['sessions_checked']}, "
            f"ok={results['sessions_ok']}, "
            f"mismatch={results['sessions_mismatch']}"
        )
        
        return results
    
    async def _reconcile_session(self, session: Session) -> bool:
        """
        REAL reconcile single session
        Returns True if session data is consistent
        """
        # Compare local_counted_mb vs server_counted_mb
        local_mb = session.local_counted_mb or 0
        server_mb = session.server_counted_mb or 0
        
        # Calculate acceptable difference
        max_diff_percent = local_mb * self.TOLERANCE_PERCENT
        max_diff = max(max_diff_percent, self.TOLERANCE_MB)
        
        actual_diff = abs(local_mb - server_mb)
        
        if actual_diff <= max_diff:
            return True  # Within tolerance
        
        # Mismatch detected
        logger.warning(
            f"Session {session.id} mismatch: "
            f"local={local_mb}MB, server={server_mb}MB, diff={actual_diff}MB"
        )
        
        # Use server count as authoritative
        if session.estimated_earnings:
            # Recalculate earnings based on server count
            price_data = await self.pricing_service.get_current_price()
            price_per_mb = price_data["price_per_mb"]
            
            correct_earnings = server_mb * price_per_mb
            
            if abs(session.estimated_earnings - correct_earnings) > 0.001:
                logger.info(
                    f"Correcting session {session.id} earnings: "
                    f"${session.estimated_earnings:.4f} -> ${correct_earnings:.4f}"
                )
                session.estimated_earnings = correct_earnings
        
        return False  # Mismatch detected
    
    async def _reconcile_all_balances(self) -> int:
        """
        REAL reconcile all user balances
        Recalculates from transactions
        """
        result = await self.db.execute(
            select(User).where(User.is_active == True)
        )
        users = result.scalars().all()
        
        corrected_count = 0
        
        for user in users:
            try:
                corrected = await self._reconcile_user_balance(user)
                if corrected:
                    corrected_count += 1
            except Exception as e:
                logger.error(f"Balance reconciliation error for user {user.telegram_id}: {e}")
        
        return corrected_count
    
    async def _reconcile_user_balance(self, user: User) -> bool:
        """
        REAL reconcile single user balance
        Returns True if balance was corrected
        """
        # Calculate actual balance from transactions
        result = await self.db.execute(
            select(func.sum(Transaction.amount_usd))
            .where(Transaction.telegram_id == user.telegram_id)
            .where(Transaction.status == "completed")
        )
        
        total_from_transactions = result.scalar() or 0.0
        
        # Add income from completed sessions (if not in transactions)
        sessions_result = await self.db.execute(
            select(func.sum(Session.estimated_earnings))
            .where(Session.telegram_id == user.telegram_id)
            .where(Session.status == "completed")
        )
        
        total_from_sessions = sessions_result.scalar() or 0.0
        
        # Calculate expected balance
        expected_balance = total_from_transactions + total_from_sessions
        
        # Compare with current balance
        current_balance = user.balance_usd or 0.0
        
        diff = abs(expected_balance - current_balance)
        
        if diff > 0.01:  # More than 1 cent difference
            logger.warning(
                f"User {user.telegram_id} balance mismatch: "
                f"current=${current_balance:.2f}, expected=${expected_balance:.2f}"
            )
            
            # Correct the balance
            user.balance_usd = expected_balance
            user.last_balance_refresh = datetime.utcnow()
            
            logger.info(f"Corrected balance for user {user.telegram_id}")
            return True
        
        return False  # Balance is correct
    
    async def reconcile_session_reports(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        REAL reconcile session reports
        Aggregates all reports for a session
        """
        from app.models.session import SessionReport
        
        # Get all reports for session
        result = await self.db.execute(
            select(SessionReport)
            .where(SessionReport.session_id == session_id)
            .order_by(SessionReport.timestamp)
        )
        reports = result.scalars().all()
        
        if not reports:
            return {
                "status": "no_reports",
                "total_mb": 0.0
            }
        
        # Aggregate MB from reports
        total_mb = 0.0
        last_cumulative = 0.0
        
        for report in reports:
            if report.delta_mb:
                total_mb += report.delta_mb
            elif report.cumulative_mb:
                # Use delta from cumulative
                delta = report.cumulative_mb - last_cumulative
                if delta > 0:
                    total_mb += delta
                last_cumulative = report.cumulative_mb
        
        # Get session
        session_result = await self.db.execute(
            select(Session).where(Session.id == session_id)
        )
        session = session_result.scalar_one_or_none()
        
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Update server_counted_mb
        old_server_mb = session.server_counted_mb or 0.0
        session.server_counted_mb = total_mb
        
        await self.db.commit()
        
        logger.info(
            f"Session {session_id} reports reconciled: "
            f"{old_server_mb:.2f}MB -> {total_mb:.2f}MB"
        )
        
        return {
            "status": "reconciled",
            "reports_count": len(reports),
            "total_mb": total_mb,
            "old_server_mb": old_server_mb,
            "new_server_mb": total_mb
        }
