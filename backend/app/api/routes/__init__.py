"""API routers."""

from fastapi import APIRouter

from . import (
    analytics,
    auth,
    balance,
    dashboard,
    news,
    notifications,
    profile,
    settings,
    support,
    traffic,
    transactions,
    withdraw,
)


api_router = APIRouter()

api_router.include_router(auth.router, prefix="/api/auth", tags=["auth"])
api_router.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
api_router.include_router(traffic.router, prefix="/api", tags=["traffic"])
api_router.include_router(balance.router, prefix="/api", tags=["balance"])
api_router.include_router(transactions.router, prefix="/api", tags=["transactions"])
api_router.include_router(withdraw.router, prefix="/api", tags=["withdraw"])
api_router.include_router(notifications.router, prefix="/api", tags=["notifications"])
api_router.include_router(settings.router, prefix="/api", tags=["settings"])
api_router.include_router(profile.router, prefix="/api", tags=["profile"])
api_router.include_router(analytics.router, prefix="/api", tags=["analytics"])
api_router.include_router(support.router, prefix="/api", tags=["support"])
api_router.include_router(news.router, prefix="/api", tags=["news"])
