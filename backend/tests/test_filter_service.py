import pytest
from app.services.filter_service import FilterService


@pytest.mark.asyncio
async def test_check_can_start_session_admin_bypass(db_session):
    """Test admin bypass for filter checks"""
    from app.core.config import settings
    
    filter_service = FilterService(db_session)
    
    # Admin should bypass all checks
    admin_id = settings.admin_ids_list[0] if settings.admin_ids_list else 123456
    
    can_start, reason = await filter_service.check_can_start_session(
        telegram_id=admin_id,
        ip_address="1.2.3.4"
    )
    
    assert can_start is True
    assert "bypass" in reason.lower()


@pytest.mark.asyncio
async def test_check_can_start_session_no_ip(db_session):
    """Test session start fails without IP"""
    filter_service = FilterService(db_session)
    
    can_start, reason = await filter_service.check_can_start_session(
        telegram_id=999999,
        ip_address=None
    )
    
    assert can_start is False
    assert "IP" in reason


@pytest.mark.asyncio
async def test_vpn_score_calculation():
    """Test VPN score calculation"""
    filter_service = FilterService(None)
    
    # Test with proxy flag
    ip_data = {"proxy": True, "hosting": False, "isp": "normal"}
    score = await filter_service._calculate_vpn_score(ip_data)
    assert score >= 50
    
    # Test with datacenter
    ip_data = {"proxy": False, "hosting": True, "isp": "normal"}
    score = await filter_service._calculate_vpn_score(ip_data)
    assert score >= 40
    
    # Test with VPN keywords in ISP
    ip_data = {"proxy": False, "hosting": False, "isp": "VPN Provider Inc"}
    score = await filter_service._calculate_vpn_score(ip_data)
    assert score >= 20
