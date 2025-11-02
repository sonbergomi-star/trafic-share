from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.user import (
    LoginHistoryEntry,
    LoginHistoryResponse,
    LogoutResponse,
    SettingsPayload,
    SettingsResponse,
    TokenRenewResponse,
    UserDetail,
)
from app.services.user_service import UserService


router = APIRouter(prefix="/api/user", tags=["user"])


@router.get("/profile", response_model=UserDetail)
def get_profile(current_user=Depends(get_current_user)):
    return UserDetail.model_validate(current_user)


@router.patch("/settings", response_model=SettingsResponse)
def update_settings(
    payload: SettingsPayload,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return UserService.update_settings(current_user, payload, db)


@router.post("/token/renew", response_model=TokenRenewResponse)
def renew_token(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return UserService.renew_token(current_user, db)


@router.post("/logout", response_model=LogoutResponse)
def logout(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    UserService.logout(current_user, db)
    return LogoutResponse(message="Successfully logged out")


@router.post("/logout_all", response_model=LogoutResponse)
def logout_all(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    UserService.logout_all(current_user, db)
    return LogoutResponse(message="All sessions terminated")


@router.get("/login_history", response_model=LoginHistoryResponse)
def login_history(current_user=Depends(get_current_user)):
    history = [
        LoginHistoryEntry(
            city="Tashkent",
            device=current_user.last_login_device,
            ip=current_user.last_login_ip,
            time=current_user.auth_date or datetime.utcnow(),
        )
    ]
    return LoginHistoryResponse(history=history)

