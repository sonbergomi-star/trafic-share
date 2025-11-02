import pytest
from datetime import date
from app.services.pricing_service import PricingService
from app.models.pricing import DailyPrice


@pytest.mark.asyncio
async def test_get_current_price_default(db_session):
    """Test get current price returns default when no price set"""
    pricing_service = PricingService(db_session)
    
    price_data = await pricing_service.get_current_price()
    
    assert price_data is not None
    assert price_data["price_per_gb"] > 0
    assert "date" in price_data


@pytest.mark.asyncio
async def test_set_daily_price(db_session, mock_admin):
    """Test setting daily price"""
    pricing_service = PricingService(db_session)
    
    result = await pricing_service.set_daily_price(
        admin_id=mock_admin.telegram_id,
        price_per_gb=1.50,
        message="Test price"
    )
    
    assert result["price_per_gb"] == 1.50
    assert result["message"] == "Test price"


@pytest.mark.asyncio
async def test_set_daily_price_validation(db_session, mock_admin):
    """Test price validation"""
    pricing_service = PricingService(db_session)
    
    # Price too low
    with pytest.raises(ValueError):
        await pricing_service.set_daily_price(
            admin_id=mock_admin.telegram_id,
            price_per_gb=0.05
        )
    
    # Price too high
    with pytest.raises(ValueError):
        await pricing_service.set_daily_price(
            admin_id=mock_admin.telegram_id,
            price_per_gb=15.00
        )


@pytest.mark.asyncio
async def test_calculate_earnings(db_session):
    """Test earnings calculation"""
    pricing_service = PricingService(db_session)
    
    # Set a known price
    await pricing_service.set_daily_price(
        admin_id=123456,
        price_per_gb=2.00  # $2 per GB = $0.001953125 per MB
    )
    
    # Calculate earnings for 1024 MB (1 GB)
    earnings = await pricing_service.calculate_earnings(1024.0)
    
    assert earnings == pytest.approx(2.0, rel=0.01)


@pytest.mark.asyncio
async def test_get_price_history(db_session, mock_admin):
    """Test getting price history"""
    pricing_service = PricingService(db_session)
    
    # Set a price
    await pricing_service.set_daily_price(
        admin_id=mock_admin.telegram_id,
        price_per_gb=1.75,
        message="History test"
    )
    
    # Get history
    history = await pricing_service.get_price_history(days=7)
    
    assert isinstance(history, list)
    assert len(history) > 0
    assert history[0]["price_per_gb"] == 1.75
