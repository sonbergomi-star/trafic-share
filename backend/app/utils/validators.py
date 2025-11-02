import re
from typing import Optional
from datetime import datetime


class Validators:
    """Validation utilities"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_telegram_id(telegram_id: int) -> bool:
        """Validate Telegram ID format"""
        # Telegram IDs are positive integers
        return isinstance(telegram_id, int) and telegram_id > 0
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Validate phone number format"""
        # Basic international format validation
        pattern = r'^\+?[1-9]\d{1,14}$'
        return bool(re.match(pattern, phone.replace(' ', '').replace('-', '')))
    
    @staticmethod
    def validate_wallet_address(address: str, network: str = "BEP20") -> bool:
        """Validate cryptocurrency wallet address"""
        if network in ["BEP20", "ERC20", "ETH"]:
            # Ethereum-compatible address
            pattern = r'^0x[a-fA-F0-9]{40}$'
            return bool(re.match(pattern, address))
        elif network == "BTC":
            # Bitcoin address (simplified)
            pattern = r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$'
            return bool(re.match(pattern, address))
        elif network == "TRC20":
            # TRON address
            pattern = r'^T[a-zA-Z0-9]{33}$'
            return bool(re.match(pattern, address))
        return False
    
    @staticmethod
    def validate_amount(amount: float, min_amount: float = 0.0, max_amount: Optional[float] = None) -> tuple[bool, str]:
        """Validate monetary amount"""
        if not isinstance(amount, (int, float)):
            return False, "Amount must be a number"
        
        if amount < min_amount:
            return False, f"Amount must be at least {min_amount}"
        
        if max_amount and amount > max_amount:
            return False, f"Amount cannot exceed {max_amount}"
        
        if amount < 0:
            return False, "Amount cannot be negative"
        
        # Check decimal places (max 2 for USD)
        if round(amount, 2) != amount:
            return False, "Amount can have at most 2 decimal places"
        
        return True, "Valid"
    
    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        """Validate username format"""
        if not username:
            return False, "Username cannot be empty"
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        
        if len(username) > 32:
            return False, "Username cannot exceed 32 characters"
        
        # Only alphanumeric and underscore
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username can only contain letters, numbers, and underscores"
        
        return True, "Valid"
    
    @staticmethod
    def validate_session_id(session_id: str) -> bool:
        """Validate session ID format (UUID)"""
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, session_id.lower()))
    
    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """Validate IP address format"""
        # IPv4
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if re.match(ipv4_pattern, ip):
            parts = ip.split('.')
            return all(0 <= int(part) <= 255 for part in parts)
        
        # IPv6 (basic check)
        ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
        return bool(re.match(ipv6_pattern, ip))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def validate_date_range(start_date: datetime, end_date: datetime) -> tuple[bool, str]:
        """Validate date range"""
        if start_date > end_date:
            return False, "Start date cannot be after end date"
        
        if end_date > datetime.utcnow():
            return False, "End date cannot be in the future"
        
        # Check if range is reasonable (not more than 1 year)
        max_days = 365
        if (end_date - start_date).days > max_days:
            return False, f"Date range cannot exceed {max_days} days"
        
        return True, "Valid"
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 1000) -> str:
        """Sanitize user input"""
        if not text:
            return ""
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Limit length
        if len(text) > max_length:
            text = text[:max_length]
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Remove control characters except newlines and tabs
        text = ''.join(char for char in text if char == '\n' or char == '\t' or ord(char) >= 32)
        
        return text
    
    @staticmethod
    def validate_traffic_amount(mb: float) -> tuple[bool, str]:
        """Validate traffic amount in MB"""
        if mb < 0:
            return False, "Traffic amount cannot be negative"
        
        if mb > 1000000:  # 1TB limit
            return False, "Traffic amount too large"
        
        return True, "Valid"
    
    @staticmethod
    def validate_speed(speed_mb_s: float) -> tuple[bool, str]:
        """Validate traffic speed in MB/s"""
        if speed_mb_s < 0:
            return False, "Speed cannot be negative"
        
        if speed_mb_s > 1000:  # 1 GB/s limit (reasonable max)
            return False, "Speed value too high"
        
        return True, "Valid"
