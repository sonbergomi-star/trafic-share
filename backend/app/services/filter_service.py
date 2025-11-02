from typing import Dict, Any, Optional
import httpx
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class FilterService:
    """Traffic start filter & VPN/Proxy detection service"""
    
    # Allowed regions (US + EU countries)
    ALLOWED_REGIONS = [
        "US",  # United States
        # EU Countries
        "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR",
        "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL",
        "PL", "PT", "RO", "SK", "SI", "ES", "SE"
    ]
    
    VPN_SCORE_BLOCK_THRESHOLD = 70
    VPN_SCORE_WARN_THRESHOLD = 50
    BLOCK_IF_PROXY = True
    ALLOWED_NETWORK_TYPES = ["mobile", "wifi"]
    
    async def check_can_start_session(
        self,
        telegram_id: int,
        ip_address: str,
        network_type: str,
        is_admin: bool = False
    ) -> Dict[str, Any]:
        """
        Check if user can start traffic session
        Admin users bypass all checks
        """
        
        # Admin bypass
        if is_admin:
            return {
                "allowed": True,
                "filter_status": "skipped",
                "reasons": ["admin_bypass"],
                "message": "Admin user - all filters bypassed"
            }
        
        reasons = []
        
        # 1. Check IP reputation
        ip_check = await self._check_ip_reputation(ip_address)
        
        # 2. Check region
        if ip_check.get("country") not in self.ALLOWED_REGIONS:
            reasons.append("region_not_allowed")
        
        # 3. Check VPN/Proxy
        if ip_check.get("is_proxy"):
            reasons.append("proxy_detected")
        
        vpn_score = ip_check.get("vpn_score", 0)
        if vpn_score > self.VPN_SCORE_BLOCK_THRESHOLD:
            reasons.append("vpn_detected")
        
        # 4. Check network type
        if network_type not in self.ALLOWED_NETWORK_TYPES:
            reasons.append("invalid_network_type")
        
        # 5. Check datacenter IP
        if ip_check.get("is_datacenter"):
            reasons.append("datacenter_ip")
        
        # Decision
        if reasons:
            return {
                "allowed": False,
                "filter_status": "failed",
                "reasons": reasons,
                "message": self._get_error_message(reasons),
                "ip_data": ip_check
            }
        
        return {
            "allowed": True,
            "filter_status": "passed",
            "reasons": [],
            "message": "All checks passed",
            "ip_data": ip_check
        }
    
    async def _check_ip_reputation(self, ip_address: str) -> Dict[str, Any]:
        """
        Check IP reputation using various services
        Mock implementation - in production use real services:
        - MaxMind GeoIP2
        - IPQualityScore
        - ipinfo.io
        - AbuseIPDB
        """
        
        try:
            # Using ip-api.com (free tier)
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://ip-api.com/json/{ip_address}",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse response
                    return {
                        "ip": ip_address,
                        "country": data.get("countryCode"),
                        "region": data.get("regionName"),
                        "city": data.get("city"),
                        "isp": data.get("isp"),
                        "asn": data.get("as"),
                        "is_proxy": data.get("proxy", False),
                        "is_datacenter": self._is_datacenter_isp(data.get("isp", "")),
                        "vpn_score": self._calculate_vpn_score(data),
                    }
        
        except Exception as e:
            logger.error(f"IP check failed: {e}")
        
        # Fallback - allow by default if check fails
        return {
            "ip": ip_address,
            "country": "US",
            "is_proxy": False,
            "is_datacenter": False,
            "vpn_score": 0,
            "check_failed": True
        }
    
    def _is_datacenter_isp(self, isp_name: str) -> bool:
        """Check if ISP is a datacenter"""
        datacenter_keywords = [
            "amazon", "aws", "azure", "google cloud", "digitalocean",
            "linode", "vultr", "ovh", "hetzner", "contabo"
        ]
        isp_lower = isp_name.lower()
        return any(keyword in isp_lower for keyword in datacenter_keywords)
    
    def _calculate_vpn_score(self, ip_data: Dict[str, Any]) -> float:
        """
        Calculate VPN probability score (0-100)
        Higher score = more likely to be VPN/Proxy
        """
        score = 0.0
        
        # Check proxy flag
        if ip_data.get("proxy"):
            score += 80
        
        # Check if mobile network
        if ip_data.get("mobile"):
            score -= 20  # Less likely to be VPN
        
        # Check ISP
        isp = ip_data.get("isp", "").lower()
        if any(word in isp for word in ["vpn", "proxy", "private"]):
            score += 60
        
        # Ensure score is in range 0-100
        return max(0.0, min(100.0, score))
    
    def _get_error_message(self, reasons: list) -> str:
        """Get user-friendly error message"""
        messages = {
            "vpn_detected": "VPN yoki proxy aniqlandi. Iltimos, to'g'ridan-to'g'ri internet orqali ulaning.",
            "proxy_detected": "Proxy server aniqlandi. Iltimos, to'g'ridan-to'g'ri ulanishdan foydalaning.",
            "region_not_allowed": "Sizning mintaqangizdan foydalanish mumkin emas. Faqat US va EU mintaqalaridan.",
            "datacenter_ip": "Datacenter IP aniqlandi. Iltimos, uy yoki mobil internetdan foydalaning.",
            "invalid_network_type": "Tarmoq turi qo'llab-quvvatlanmaydi. Faqat WiFi yoki mobil internet.",
        }
        
        if not reasons:
            return "Xatolik yuz berdi"
        
        return messages.get(reasons[0], "Ulanish ta'qiqlangan")
