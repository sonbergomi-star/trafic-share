from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models.traffic import TrafficSession
from app.db.session import get_db
from app.schemas.dashboard import StartTrafficRequest, StartTrafficResponse, StopTrafficRequest, StopTrafficResponse
from app.schemas.traffic import ReportIngestRequest, SessionReportSchema
from app.services.traffic_service import TrafficService


router = APIRouter(prefix="/api/traffic", tags=["traffic"])


@router.post("/start", response_model=StartTrafficResponse)
def start_traffic(
    payload: StartTrafficRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        session = TrafficService.start_session(current_user, payload, db)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    bypass = session.filter_status == "skipped"
    return StartTrafficResponse(status="ok", session_id=session.id, message="Tunnel opened", bypass=bypass)


@router.post("/stop", response_model=StopTrafficResponse)
def stop_traffic(payload: StopTrafficRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    session = TrafficService.stop_session(payload.session_id, db)
    if session.telegram_id != current_user.telegram_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    return StopTrafficResponse(
        status=session.status,
        session_id=session.id,
        sent_mb=session.sent_mb,
        used_mb=session.used_mb,
        earned_usd=session.earned_usd,
    )


@router.post("/report", response_model=SessionReportSchema)
def report(payload: ReportIngestRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.get(TrafficSession, payload.session_id)
    # Quick permission check
    if session and session.telegram_id != current_user.telegram_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    report_obj = TrafficService.ingest_report(payload, db)
    return SessionReportSchema.model_validate(report_obj)

