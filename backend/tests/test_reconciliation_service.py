import pytest
from app.services.reconciliation_service import ReconciliationService
from app.models.session import Session
from datetime import datetime


@pytest.mark.asyncio
async def test_reconcile_session_within_tolerance(db_session):
    """Test session reconciliation within tolerance"""
    reconciliation_service = ReconciliationService(db_session)
    
    # Create a session with matching counts
    session = Session(
        id="test_session_1",
        telegram_id=123456,
        local_counted_mb=1000.0,
        server_counted_mb=1002.0,  # 2 MB difference (within 5 MB tolerance)
        status="completed",
        started_at=datetime.utcnow()
    )
    db_session.add(session)
    await db_session.commit()
    
    # Reconcile
    is_ok = await reconciliation_service._reconcile_session(session)
    
    assert is_ok is True


@pytest.mark.asyncio
async def test_reconcile_session_mismatch(db_session):
    """Test session reconciliation with mismatch"""
    reconciliation_service = ReconciliationService(db_session)
    
    # Create a session with large mismatch
    session = Session(
        id="test_session_2",
        telegram_id=123456,
        local_counted_mb=1000.0,
        server_counted_mb=900.0,  # 100 MB difference (exceeds tolerance)
        status="completed",
        started_at=datetime.utcnow()
    )
    db_session.add(session)
    await db_session.commit()
    
    # Reconcile
    is_ok = await reconciliation_service._reconcile_session(session)
    
    assert is_ok is False


@pytest.mark.asyncio
async def test_reconcile_user_balance(db_session, mock_user):
    """Test user balance reconciliation"""
    reconciliation_service = ReconciliationService(db_session)
    
    # Set initial balance
    mock_user.balance_usd = 0.0
    
    # Create completed session with earnings
    session = Session(
        id="test_earnings_session",
        telegram_id=mock_user.telegram_id,
        server_counted_mb=1024.0,
        estimated_earnings=2.0,
        status="completed",
        started_at=datetime.utcnow()
    )
    db_session.add(session)
    await db_session.commit()
    
    # Reconcile balance
    corrected = await reconciliation_service._reconcile_user_balance(mock_user)
    
    assert corrected is True
    assert mock_user.balance_usd > 0
