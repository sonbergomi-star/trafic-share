"""FastAPI application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings
from app.core.logging import setup_logging


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title=settings.app_name, version="0.1.0")

    if settings.allowed_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.allowed_origins],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(api_router)

    @app.get("/health", tags=["health"])
    async def health_check():
        return {"status": "ok"}

    return app


app = create_app()
