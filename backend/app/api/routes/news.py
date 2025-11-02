"""News & promo endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.services.news_service import NewsService


router = APIRouter()


@router.get("/news_promo")
async def news_promo(session: AsyncSession = Depends(get_db_session)):
    service = NewsService(session)
    return await service.get_feed()
