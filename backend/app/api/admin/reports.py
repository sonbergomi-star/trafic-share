from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date

from app.core.database import get_db
from app.middleware.auth import verify_admin
from app.models.user import User
from app.services.admin_service import AdminService
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/admin/reports", tags=["Admin - Reports"])


@router.get("/dashboard")
async def get_dashboard_stats(
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get admin dashboard statistics (Admin only)
    """
    admin_service = AdminService(db)
    result = await admin_service.get_dashboard_stats()
    
    return {
        "status": "success",
        "data": result
    }


@router.get("/platform-analytics")
async def get_platform_analytics(
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get platform-wide analytics (Admin only)
    """
    analytics_service = AnalyticsService(db)
    result = await analytics_service.get_platform_analytics()
    
    return {
        "status": "success",
        "data": result
    }


@router.get("/traffic-trends")
async def get_traffic_trends(
    days: int = 30,
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get traffic trends (Admin only)
    """
    analytics_service = AnalyticsService(db)
    result = await analytics_service.get_traffic_trends(days=days)
    
    return {
        "status": "success",
        "data": result
    }


@router.get("/top-users")
async def get_top_users(
    period: str = "month",
    limit: int = 10,
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get top users by earnings (Admin only)
    """
    analytics_service = AnalyticsService(db)
    result = await analytics_service.get_user_ranking(
        period=period,
        limit=limit
    )
    
    return {
        "status": "success",
        "data": result
    }


@router.get("/export/users")
async def export_users(
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Export users data as CSV (Admin only)
    """
    admin_service = AdminService(db)
    csv_content = await admin_service.export_users_csv()
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=users_export.csv"
        }
    )


@router.get("/export/sessions")
async def export_sessions(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Export sessions data as CSV (Admin only)
    """
    admin_service = AdminService(db)
    csv_content = await admin_service.export_sessions_csv(
        start_date=start_date,
        end_date=end_date
    )
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=sessions_export.csv"
        }
    )


@router.get("/system-health")
async def get_system_health(
    admin: User = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get system health metrics (Admin only)
    """
    admin_service = AdminService(db)
    result = await admin_service.get_system_health()
    
    return {
        "status": "success",
        "data": result
    }
