from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.middleware.auth import verify_admin
from app.models.user import User
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin/withdrawals", tags=["Admin - Withdrawals"])


@router.get("/pending")
async def get_pending_withdrawals(
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all pending withdrawal requests (Admin only)
    """
    admin_service = AdminService(db)
    result = await admin_service.get_pending_withdrawals()
    
    return {
        "status": "success",
        "data": result
    }


@router.post("/{withdraw_id}/approve")
async def approve_withdrawal(
    withdraw_id: int,
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Approve a withdrawal request (Admin only)
    """
    admin_service = AdminService(db)
    result = await admin_service.approve_withdrawal(
        withdraw_id=withdraw_id,
        admin_id=admin.telegram_id
    )
    
    return {
        "status": "success",
        "data": result
    }


@router.post("/{withdraw_id}/reject")
async def reject_withdrawal(
    withdraw_id: int,
    reason: str,
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Reject a withdrawal request (Admin only)
    """
    admin_service = AdminService(db)
    result = await admin_service.reject_withdrawal(
        withdraw_id=withdraw_id,
        admin_id=admin.telegram_id,
        reason=reason
    )
    
    return {
        "status": "success",
        "data": result
    }
