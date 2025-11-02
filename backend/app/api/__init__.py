from fastapi import APIRouter

from app.api.routes import (
    admin,
    analytics,
    auth,
    balance,
    dashboard,
    news,
    notifications,
    pricing,
    sessions,
    support,
    traffic,
    user,
)


api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(traffic.router)
api_router.include_router(balance.router)
api_router.include_router(pricing.router)
api_router.include_router(notifications.router)
api_router.include_router(support.router)
api_router.include_router(news.router)
api_router.include_router(user.router)
api_router.include_router(analytics.router)
api_router.include_router(admin.router)
api_router.include_router(sessions.router)

