from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import AuthResponse, TelegramAuthPayload, UserProfile
from app.services.auth_service import AuthService


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/telegram", response_model=AuthResponse)
def telegram_auth(payload: TelegramAuthPayload, db: Session = Depends(get_db)):
    try:
        user = AuthService.authenticate(payload, db)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    token = AuthService.issue_token(user)
    user.jwt_token = token
    db.commit()

    user_profile = UserProfile.model_validate(user)
    return AuthResponse(user=user_profile, token=token)

