"""Database engine and session utilities."""

from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings


engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield an async database session for dependency injection."""

    async with async_session_factory() as session:
        yield session
