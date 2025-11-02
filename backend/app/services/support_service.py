"""Support ticket service."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SupportRequest, SupportStatus, User
from app.schemas.support import SupportCreateRequest


class SupportService:
    """Handles support ticket CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_ticket(self, user: User, payload: SupportCreateRequest) -> SupportRequest:
        ticket = SupportRequest(
            user_id=user.id,
            subject=payload.subject,
            message=payload.message,
            attachment_url=payload.attachment_url,
            status=SupportStatus.NEW,
        )
        self.session.add(ticket)
        await self.session.commit()
        await self.session.refresh(ticket)
        return ticket

    async def list_tickets(self, user: User) -> list[SupportRequest]:
        stmt = (
            select(SupportRequest)
            .where(SupportRequest.user_id == user.id)
            .order_by(SupportRequest.created_at.desc())
        )
        return (await self.session.execute(stmt)).scalars().all()
