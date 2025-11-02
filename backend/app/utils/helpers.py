from datetime import datetime, timedelta, date
from typing import Optional, Dict, Any, List
import hashlib
import secrets
import string
import uuid


class Helpers:
    """Helper utility functions"""
    
    @staticmethod
    def generate_unique_id() -> str:
        """Generate a unique UUID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_api_key(length: int = 32) -> str:
        """Generate a random API key"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def hash_string(text: str, algorithm: str = 'sha256') -> str:
        """Hash a string using specified algorithm"""
        if algorithm == 'md5':
            return hashlib.md5(text.encode()).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(text.encode()).hexdigest()
        elif algorithm == 'sha256':
            return hashlib.sha256(text.encode()).hexdigest()
        elif algorithm == 'sha512':
            return hashlib.sha512(text.encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    @staticmethod
    def truncate_string(text: str, max_length: int = 50, suffix: str = '...') -> str:
        """Truncate string to max length"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def mask_string(text: str, visible_chars: int = 4, mask_char: str = '*') -> str:
        """Mask a string, showing only first/last characters"""
        if len(text) <= visible_chars * 2:
            return text
        
        start = text[:visible_chars]
        end = text[-visible_chars:]
        middle = mask_char * (len(text) - visible_chars * 2)
        
        return f"{start}{middle}{end}"
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """Format duration in seconds to human-readable format"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}m {secs}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{hours}h {minutes}m {secs}s"
    
    @staticmethod
    def calculate_duration(start: datetime, end: datetime) -> str:
        """Calculate duration between two datetimes"""
        delta = end - start
        total_seconds = int(delta.total_seconds())
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    @staticmethod
    def mb_to_gb(mb: float) -> float:
        """Convert MB to GB"""
        return round(mb / 1024, 2)
    
    @staticmethod
    def gb_to_mb(gb: float) -> float:
        """Convert GB to MB"""
        return round(gb * 1024, 2)
    
    @staticmethod
    def bytes_to_mb(bytes_count: int) -> float:
        """Convert bytes to MB"""
        return round(bytes_count / (1024 * 1024), 2)
    
    @staticmethod
    def mb_to_bytes(mb: float) -> int:
        """Convert MB to bytes"""
        return int(mb * 1024 * 1024)
    
    @staticmethod
    def format_file_size(bytes_count: int) -> str:
        """Format bytes to human-readable file size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.2f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.2f} PB"
    
    @staticmethod
    def calculate_percentage(part: float, total: float) -> float:
        """Calculate percentage"""
        if total == 0:
            return 0.0
        return round((part / total) * 100, 2)
    
    @staticmethod
    def calculate_earnings(mb: float, price_per_mb: float) -> float:
        """Calculate earnings from traffic"""
        return round(mb * price_per_mb, 6)
    
    @staticmethod
    def get_date_range(days: int) -> tuple[date, date]:
        """Get date range from today going back N days"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        return start_date, end_date
    
    @staticmethod
    def get_week_start_end() -> tuple[date, date]:
        """Get current week start and end dates"""
        today = date.today()
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        return start, end
    
    @staticmethod
    def get_month_start_end() -> tuple[date, date]:
        """Get current month start and end dates"""
        today = date.today()
        start = date(today.year, today.month, 1)
        
        # Get last day of month
        if today.month == 12:
            end = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(today.year, today.month + 1, 1) - timedelta(days=1)
        
        return start, end
    
    @staticmethod
    def parse_telegram_auth_date(auth_date: int) -> datetime:
        """Parse Telegram auth_date (Unix timestamp) to datetime"""
        return datetime.fromtimestamp(auth_date)
    
    @staticmethod
    def get_time_ago(dt: datetime) -> str:
        """Get human-readable time ago string"""
        now = datetime.utcnow()
        delta = now - dt
        
        seconds = int(delta.total_seconds())
        
        if seconds < 60:
            return f"{seconds} soniya oldin"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes} daqiqa oldin"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours} soat oldin"
        elif seconds < 604800:
            days = seconds // 86400
            return f"{days} kun oldin"
        else:
            return dt.strftime("%Y-%m-%d")
    
    @staticmethod
    def chunk_list(lst: List, chunk_size: int) -> List[List]:
        """Split list into chunks"""
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
    
    @staticmethod
    def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
        """Safe division that returns default on division by zero"""
        try:
            return numerator / denominator if denominator != 0 else default
        except (ZeroDivisionError, TypeError):
            return default
    
    @staticmethod
    def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
        """Merge two dictionaries"""
        result = dict1.copy()
        result.update(dict2)
        return result
    
    @staticmethod
    def remove_none_values(data: Dict) -> Dict:
        """Remove None values from dictionary"""
        return {k: v for k, v in data.items() if v is not None}
    
    @staticmethod
    def generate_reference_id(prefix: str = "REF") -> str:
        """Generate a reference ID with prefix"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        random_part = secrets.token_hex(4).upper()
        return f"{prefix}_{timestamp}_{random_part}"
