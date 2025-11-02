from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api.auth import router as auth_router
from app.api.dashboard import router as dashboard_router
from app.api.balance import router as balance_router
from app.api.withdraw import router as withdraw_router
from app.api.stats import router as stats_router
from app.api.sessions import router as sessions_router
from app.api.support import router as support_router
from app.api.news import router as news_router
from app.api.profile import router as profile_router
from app.api.admin import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Traffic Sharing Platform...")
    print(f"📌 Version: {settings.APP_VERSION}")
    print(f"🌐 VPS IP: {settings.VPS_IP}")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": str(exc)}
    )


# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}


# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(balance_router, prefix="/api/balance", tags=["Balance"])
app.include_router(withdraw_router, prefix="/api/withdraw", tags=["Withdraw"])
app.include_router(stats_router, prefix="/api/stats", tags=["Statistics"])
app.include_router(sessions_router, prefix="/api/sessions", tags=["Sessions"])
app.include_router(support_router, prefix="/api/support", tags=["Support"])
app.include_router(news_router, prefix="/api/news", tags=["News & Promo"])
app.include_router(profile_router, prefix="/api/profile", tags=["Profile"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
