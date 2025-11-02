from fastapi import APIRouter
from app.api.v1 import auth, dashboard, traffic, balance, withdraw, statistics, settings, sessions, support, news, profile, admin, daily_price

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(traffic.router, prefix="/traffic", tags=["traffic"])
api_router.include_router(balance.router, prefix="/user", tags=["balance"])
api_router.include_router(withdraw.router, prefix="/withdraw", tags=["withdraw"])
api_router.include_router(statistics.router, prefix="/stats", tags=["statistics"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(support.router, prefix="/support", tags=["support"])
api_router.include_router(news.router, prefix="/news", tags=["news"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(daily_price.router, prefix="", tags=["daily_price"])
