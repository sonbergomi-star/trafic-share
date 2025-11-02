import pytest
from app.services.notification_service import NotificationService
from app.models.notification import FCMToken


@pytest.mark.asyncio
async def test_register_device(db_session, mock_user):
    """Test device token registration"""
    notif_service = NotificationService(db_session)
    
    result = await notif_service.register_device(
        telegram_id=mock_user.telegram_id,
        fcm_token="test_token_123",
        device_info="Test Device"
    )
    
    assert result["status"] == "success"
    
    # Verify token was saved
    from sqlalchemy import select
    token_result = await db_session.execute(
        select(FCMToken).where(FCMToken.token == "test_token_123")
    )
    token = token_result.scalar_one_or_none()
    
    assert token is not None
    assert token.telegram_id == mock_user.telegram_id


@pytest.mark.asyncio
async def test_send_to_user_no_tokens(db_session):
    """Test sending notification to user with no tokens"""
    notif_service = NotificationService(db_session)
    
    success = await notif_service.send_to_user(
        telegram_id=999999,
        title="Test",
        body="Test body",
        notif_type="test"
    )
    
    assert success is False


@pytest.mark.asyncio
async def test_send_balance_update(db_session, mock_user):
    """Test balance update notification"""
    notif_service = NotificationService(db_session)
    
    # Register a token first
    await notif_service.register_device(
        telegram_id=mock_user.telegram_id,
        fcm_token="test_balance_token",
        device_info="Test"
    )
    
    await notif_service.send_balance_update(
        telegram_id=mock_user.telegram_id,
        amount=5.50,
        new_balance=10.00
    )
    
    # Check notification was created
    from sqlalchemy import select
    from app.models.notification import Notification
    
    result = await db_session.execute(
        select(Notification)
        .where(Notification.telegram_id == mock_user.telegram_id)
        .where(Notification.type == "balance_updated")
    )
    notification = result.scalar_one_or_none()
    
    assert notification is not None
    assert "5.50" in notification.body


@pytest.mark.asyncio
async def test_send_withdraw_status(db_session, mock_user):
    """Test withdraw status notification"""
    notif_service = NotificationService(db_session)
    
    await notif_service.register_device(
        telegram_id=mock_user.telegram_id,
        fcm_token="test_withdraw_token"
    )
    
    await notif_service.send_withdraw_status(
        telegram_id=mock_user.telegram_id,
        withdraw_id=1,
        status="completed",
        amount=10.00,
        tx_hash="0xabc123"
    )
    
    # Verify notification
    from sqlalchemy import select
    from app.models.notification import Notification
    
    result = await db_session.execute(
        select(Notification)
        .where(Notification.telegram_id == mock_user.telegram_id)
        .where(Notification.type == "withdraw_status")
    )
    notification = result.scalar_one_or_none()
    
    assert notification is not None
    assert "10.00" in notification.body
