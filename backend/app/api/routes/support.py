"""Support routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.schemas import SupportCreateRequest, SupportItemResponse
from app.services.support_service import SupportService


router = APIRouter()


@router.post("/support/send", response_model=SupportItemResponse)
async def send_support(
    payload: SupportCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    service = SupportService(session)
    ticket = await service.create_ticket(current_user, payload)
    return SupportItemResponse(
        id=ticket.id,
        subject=ticket.subject,
        message=ticket.message,
        status=ticket.status.value,
        attachment_url=ticket.attachment_url,
        admin_reply=ticket.admin_reply,
        created_at=ticket.created_at,
    )


@router.get("/support/history", response_model=list[SupportItemResponse])
async def support_history(
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    service = SupportService(session)
    items = await service.list_tickets(current_user)
    return [
        SupportItemResponse(
            id=item.id,
            subject=item.subject,
            message=item.message,
            status=item.status.value,
            attachment_url=item.attachment_url,
            admin_reply=item.admin_reply,
            created_at=item.created_at,
        )
        for item in items
    ]
