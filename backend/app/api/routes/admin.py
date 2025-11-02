from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.schemas.admin import AdminDashboardMetric, DashboardChartsResponse
from app.services.admin_service import AdminService


router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/dashboard/summary", response_model=AdminDashboardMetric)
def dashboard_summary(admin=Depends(require_admin), db: Session = Depends(get_db)):
    return AdminService.dashboard_summary(db)


@router.get("/dashboard/charts", response_model=DashboardChartsResponse)
def dashboard_charts(admin=Depends(require_admin), db: Session = Depends(get_db)):
    return AdminService.dashboard_charts(db)

