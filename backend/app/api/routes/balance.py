from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.finance import (
    BalanceOverview,
    RefreshBalancePayload,
    RefreshBalanceResponse,
    TransactionsResponse,
)
from app.schemas.finance import WithdrawListResponse, WithdrawPayload, WithdrawResponse
from app.services.balance_service import BalanceService
from app.services.withdraw_service import WithdrawService
from app.services.user_service import UserService


router = APIRouter(prefix="/api", tags=["balance"])


@router.get("/user/balance/{telegram_id}", response_model=BalanceOverview)
def balance_overview(
    telegram_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.telegram_id != telegram_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    target_user = current_user
    if current_user.telegram_id != telegram_id:
        try:
            target_user = UserService.get_by_telegram_id(telegram_id, db)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return BalanceService.overview(target_user, db)


@router.post("/user/refresh_balance", response_model=RefreshBalanceResponse)
def refresh_balance(
    payload: RefreshBalancePayload,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.telegram_id != current_user.telegram_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    target_user = current_user
    if payload.telegram_id != current_user.telegram_id:
        try:
            target_user = UserService.get_by_telegram_id(payload.telegram_id, db)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return BalanceService.refresh_balance(target_user, payload.delta, db)


@router.get("/transactions", response_model=TransactionsResponse)
def transactions(limit: int = 10, offset: int = 0, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return BalanceService.get_transactions(current_user, limit, offset, db)


@router.post("/withdraw", response_model=WithdrawResponse)
def withdraw(payload: WithdrawPayload, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.telegram_id != current_user.telegram_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        return WithdrawService.create_withdraw(current_user, payload, db)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/withdraws", response_model=WithdrawListResponse)
def withdraws(limit: int = 10, offset: int = 0, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return WithdrawService.list_withdraws(current_user, limit, offset, db)

