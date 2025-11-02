"""Traffic session routes."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.core.cache import redis_dependency
from app.schemas import SessionReportIn, SessionReportResponse, SessionStartRequest, SessionStopRequest
from app.services.traffic_service import TrafficService


router = APIRouter()


@router.post("/traffic/start")
async def start_traffic(
    payload: SessionStartRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    redis=Depends(redis_dependency),
    current_user=Depends(get_current_user),
):
    service = TrafficService(session, redis)
    return await service.start_session(current_user, payload, request.client.host if request.client else None)


@router.post("/traffic/stop")
async def stop_traffic(
    payload: SessionStopRequest,
    session: AsyncSession = Depends(get_db_session),
    redis=Depends(redis_dependency),
    current_user=Depends(get_current_user),
):
    service = TrafficService(session, redis)
    return await service.stop_session(current_user, payload.session_id)


@router.post("/traffic/report", response_model=SessionReportResponse)
async def report_traffic(
    payload: SessionReportIn,
    session: AsyncSession = Depends(get_db_session),
    redis=Depends(redis_dependency),
    current_user=Depends(get_current_user),
):
    service = TrafficService(session, redis)
    result = await service.record_report(current_user, payload)
    return SessionReportResponse(**result)
