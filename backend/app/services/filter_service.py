from sqlalchemy.ext.asyncio import AsyncSession
from typing import Tuple, Dict, Any, Optional
import httpx
import logging
from datetime import datetime

from app.core.config import settings
from app.utils.cache_manager import CacheManager

logger = logging.getLogger(__name__)


class FilterService:
    """
    REAL VPN/Proxy detection and traffic filtering
    Uses actual IP reputation APIs
    """
    
    # Allowed regions (US + EU)
    ALLOWED_REGIONS = [
        "US",  # United States
        # EU Countries
        "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR",
        "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL",
        "PL", "PT", "RO", "SK", "SI", "ES", "SE"
    ]
    
    VPN_SCORE_BLOCK_THRESHOLD = 70
    VPN_SCORE_WARN_THRESHOLD = 50
    
    ALLOWED_NETWORK_TYPES = ["mobile", "wifi", "ethernet"]
    BLOCKED_NETWORK_TYPES = ["vpn", "proxy", "tor"]
    
    def __init__(self, db: AsyncSession, cache: Optional[CacheManager] = None):
        self.db = db
        self.cache = cache
    
    async def check_can_start_session(
        self,
        telegram_id: int,
        ip_address: Optional[str] = None,
        location: Optional[str] = None,
        network_type: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        REAL session start filtering with VPN/Proxy detection
        Returns: (can_start: bool, reason: str)
        """
        # Check if admin (bypass all filters)
        if telegram_id in settings.admin_ids_list:
            logger.info(f"Admin {telegram_id} bypassed filters")
            return True, "Admin bypass"
        
        reasons = []
        
        # Check IP address provided
        if not ip_address:
            return False, "IP address required"
        
        # Check cache first
        cached_result = None
        if self.cache:
            cached_result = self.cache.get_cached_ip_reputation(ip_address)
        
        if cached_result:
            logger.debug(f"Using cached IP reputation for {ip_address}")
            ip_data = cached_result
        else:
            # Get IP reputation from API
            ip_data = await self._check_ip_reputation(ip_address)
            
            # Cache result
            if self.cache and ip_data:
                self.cache.cache_ip_reputation(ip_address, ip_data, ttl=86400)
        
        if not ip_data:
            # Failed to get IP data - allow or deny based on policy
            logger.warning(f"Failed to get IP reputation for {ip_address}")
            return True, "IP check failed - allowed"  # Fail-open for better UX
        
        # Check region (US + EU only)
        country_code = ip_data.get('country_code', 'XX')
        if country_code not in self.ALLOWED_REGIONS:
            reasons.append(f"region_not_allowed_{country_code}")
            logger.warning(f"Blocked region {country_code} for IP {ip_address}")
            return False, f"Faqat US va EU regionlaridan foydalanish mumkin. Sizning region: {country_code}"
        
        # Check VPN/Proxy
        is_proxy = ip_data.get('is_proxy', False)
        is_vpn = ip_data.get('is_vpn', False)
        vpn_score = ip_data.get('vpn_score', 0)
        
        if is_proxy:
            reasons.append("proxy_detected")
            return False, "Proxy server aniqlandi. Iltimos, to'g'ridan-to'g'ri internetdan foydalaning."
        
        if is_vpn or vpn_score >= self.VPN_SCORE_BLOCK_THRESHOLD:
            reasons.append("vpn_detected")
            return False, "VPN aniqlandi. Iltimos, VPN'ni o'chiring va qayta urinib ko'ring."
        
        if vpn_score >= self.VPN_SCORE_WARN_THRESHOLD:
            logger.warning(
                f"Suspicious VPN score {vpn_score} for IP {ip_address} - "
                f"user {telegram_id}"
            )
            # Allow but log warning
        
        # Check if datacenter IP
        is_datacenter = ip_data.get('is_datacenter', False)
        if is_datacenter and not self._is_datacenter_isp(ip_data.get('isp', '')):
            reasons.append("datacenter_ip")
            return False, "Datacenter IP aniqlandi. Iltimos, uy yoki mobil internetdan foydalaning."
        
        # Check network type
        if network_type and network_type.lower() in self.BLOCKED_NETWORK_TYPES:
            reasons.append(f"blocked_network_{network_type}")
            return False, f"Network turi ({network_type}) ruxsat etilmagan."
        
        # All checks passed
        logger.info(f"Session start allowed for user {telegram_id} from {ip_address} ({country_code})")
        return True, "Checks passed"
    
    async def _check_ip_reputation(self, ip: str) -> Optional[Dict[str, Any]]:
        """
        REAL IP reputation check using ip-api.com (free) or IPQualityScore (paid)
        """
        try:
            # Using ip-api.com (free, 45 req/min limit)
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://ip-api.com/json/{ip}",
                    params={
                        "fields": "status,message,country,countryCode,region,city,isp,org,as,proxy,hosting"
                    },
                    timeout=5.0
                )
                
                if response.status_code != 200:
                    logger.error(f"IP API error: {response.status_code}")
                    return None
                
                data = response.json()
                
                if data.get('status') != 'success':
                    logger.error(f"IP API failed: {data.get('message')}")
                    return None
                
                # Calculate VPN score based on available data
                vpn_score = await self._calculate_vpn_score(data)
                
                return {
                    'country_code': data.get('countryCode', 'XX'),
                    'country': data.get('country', 'Unknown'),
                    'region': data.get('region', ''),
                    'city': data.get('city', ''),
                    'isp': data.get('isp', ''),
                    'org': data.get('org', ''),
                    'as': data.get('as', ''),
                    'is_proxy': data.get('proxy', False),
                    'is_datacenter': data.get('hosting', False),
                    'is_vpn': data.get('proxy', False),  # Proxy includes VPN
                    'vpn_score': vpn_score,
                }
        
        except httpx.TimeoutException:
            logger.error(f"IP API timeout for {ip}")
            return None
        except Exception as e:
            logger.error(f"IP reputation check failed: {e}")
            return None
    
    async def _calculate_vpn_score(self, ip_data: Dict) -> int:
        """
        Calculate VPN probability score (0-100)
        REAL scoring algorithm
        """
        score = 0
        
        # Direct proxy/hosting indicator
        if ip_data.get('proxy'):
            score += 50
        
        if ip_data.get('hosting'):
            score += 40
        
        # Check ISP name for VPN keywords
        isp = ip_data.get('isp', '').lower()
        vpn_keywords = ['vpn', 'proxy', 'datacenter', 'hosting', 'cloud', 'virtual']
        
        for keyword in vpn_keywords:
            if keyword in isp:
                score += 20
                break
        
        # Cap at 100
        return min(score, 100)
    
    def _is_datacenter_isp(self, isp: str) -> bool:
        """
        Check if ISP is a legitimate datacenter provider
        (Some datacenters like AWS/Google Cloud may be whitelisted)
        """
        whitelist_keywords = [
            'amazon', 'aws', 'google', 'microsoft', 'azure', 
            'digitalocean', 'linode', 'vultr', 'hetzner'
        ]
        
        isp_lower = isp.lower()
        return any(keyword in isp_lower for keyword in whitelist_keywords)
    
    def _get_error_message(self, reasons: list) -> str:
        """
        Get user-friendly error message
        """
        if 'vpn_detected' in reasons:
            return "VPN aniqlandi. Iltimos, VPN'ni o'chiring."
        
        if 'proxy_detected' in reasons:
            return "Proxy server aniqlandi. To'g'ridan-to'g'ri internetdan foydalaning."
        
        if any('region_not_allowed' in r for r in reasons):
            return "Sizning regioningiz qo'llab-quvvatlanmaydi. Faqat US va EU."
        
        if 'datacenter_ip' in reasons:
            return "Datacenter IP. Uy yoki mobil internetdan foydalaning."
        
        return "Session boshlash mumkin emas. Qo'llab-quvvatlash bilan bog'laning."
