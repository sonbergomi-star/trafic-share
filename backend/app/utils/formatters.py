from datetime import datetime, date
from typing import Optional, Dict, Any
from decimal import Decimal


class Formatters:
    """Data formatting utilities"""
    
    @staticmethod
    def format_currency(amount: float, currency: str = "USD", symbol: str = "$") -> str:
        """Format amount as currency"""
        if currency == "USD":
            return f"{symbol}{amount:,.2f}"
        elif currency == "USDT":
            return f"{amount:,.2f} USDT"
        elif currency == "UZS":
            return f"{amount:,.0f} so'm"
        else:
            return f"{amount:,.2f} {currency}"
    
    @staticmethod
    def format_traffic(mb: float, precision: int = 2) -> str:
        """Format traffic amount"""
        if mb < 1024:
            return f"{mb:.{precision}f} MB"
        else:
            gb = mb / 1024
            return f"{gb:.{precision}f} GB"
    
    @staticmethod
    def format_speed(mb_per_second: float) -> str:
        """Format traffic speed"""
        if mb_per_second < 1:
            kb_per_second = mb_per_second * 1024
            return f"{kb_per_second:.2f} KB/s"
        else:
            return f"{mb_per_second:.2f} MB/s"
    
    @staticmethod
    def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Format datetime to string"""
        if not dt:
            return "N/A"
        return dt.strftime(format_str)
    
    @staticmethod
    def format_date(d: date, format_str: str = "%Y-%m-%d") -> str:
        """Format date to string"""
        if not d:
            return "N/A"
        return d.strftime(format_str)
    
    @staticmethod
    def format_percentage(value: float, total: float, decimals: int = 2) -> str:
        """Format value as percentage of total"""
        if total == 0:
            return "0%"
        percentage = (value / total) * 100
        return f"{percentage:.{decimals}f}%"
    
    @staticmethod
    def format_number(number: float, decimals: int = 2, separator: str = ",") -> str:
        """Format number with thousands separator"""
        if decimals == 0:
            return f"{int(number):,}".replace(",", separator)
        else:
            formatted = f"{number:,.{decimals}f}"
            return formatted.replace(",", separator)
    
    @staticmethod
    def format_phone_number(phone: str, country_code: str = "+998") -> str:
        """Format phone number"""
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, phone))
        
        # Add country code if not present
        if not phone.startswith('+'):
            phone = f"{country_code}{digits}"
        
        return phone
    
    @staticmethod
    def format_telegram_username(username: str) -> str:
        """Format Telegram username"""
        if not username:
            return ""
        
        if not username.startswith('@'):
            return f"@{username}"
        return username
    
    @staticmethod
    def format_wallet_address(address: str, show_chars: int = 6) -> str:
        """Format wallet address for display"""
        if len(address) <= show_chars * 2:
            return address
        
        return f"{address[:show_chars]}...{address[-show_chars:]}"
    
    @staticmethod
    def format_duration_human(seconds: int) -> str:
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{seconds} soniya"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes} daqiqa"
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            if minutes > 0:
                return f"{hours} soat {minutes} daqiqa"
            return f"{hours} soat"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            if hours > 0:
                return f"{days} kun {hours} soat"
            return f"{days} kun"
    
    @staticmethod
    def format_session_status(status: str) -> str:
        """Format session status in Uzbek"""
        status_map = {
            "active": "?? Faol",
            "completed": "? Tugallangan",
            "failed": "? Xato",
            "cancelled": "? Bekor qilingan",
            "pending": "? Kutilmoqda",
        }
        return status_map.get(status, status)
    
    @staticmethod
    def format_transaction_type(type_str: str) -> str:
        """Format transaction type in Uzbek"""
        type_map = {
            "income": "?? Daromad",
            "withdraw": "?? Yechish",
            "refund": "?? Qaytarish",
            "bonus": "?? Bonus",
        }
        return type_map.get(type_str, type_str)
    
    @staticmethod
    def format_notification_type(type_str: str) -> str:
        """Format notification type"""
        type_map = {
            "balance_updated": "?? Balans yangilandi",
            "withdraw_status": "?? Yechish holati",
            "session_completed": "?? Sessiya tugadi",
            "daily_price": "?? Kunlik narx",
            "system_update": "?? Tizim yangiligi",
        }
        return type_map.get(type_str, type_str)
    
    @staticmethod
    def format_api_response(
        status: str,
        data: Optional[Any] = None,
        message: Optional[str] = None,
        errors: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Format standardized API response"""
        response = {
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if data is not None:
            response["data"] = data
        
        if message:
            response["message"] = message
        
        if errors:
            response["errors"] = errors
        
        return response
    
    @staticmethod
    def format_error_response(
        error_code: str,
        message: str,
        details: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Format error response"""
        response = {
            "status": "error",
            "error_code": error_code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if details:
            response["details"] = details
        
        return response
    
    @staticmethod
    def format_pagination(
        items: list,
        page: int,
        per_page: int,
        total: int
    ) -> Dict[str, Any]:
        """Format paginated response"""
        total_pages = (total + per_page - 1) // per_page
        
        return {
            "items": items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            }
        }
