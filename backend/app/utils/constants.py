from enum import Enum


class Constants:
    """Application constants"""
    
    # Traffic limits
    MIN_TRAFFIC_MB = 0.1
    MAX_TRAFFIC_MB = 1000000  # 1 TB
    MAX_TRAFFIC_SPEED_MB_S = 1000  # 1 GB/s
    
    # Withdraw limits
    MIN_WITHDRAW_USD = 1.39
    MAX_WITHDRAW_USD = 100.00
    WITHDRAW_FEE_PERCENT = 0.0  # No fee
    
    # Session limits
    MAX_ACTIVE_SESSIONS_PER_USER = 5
    SESSION_TIMEOUT_MINUTES = 120  # 2 hours
    SESSION_HEARTBEAT_INTERVAL_SECONDS = 30
    
    # Rate limiting
    MAX_API_REQUESTS_PER_MINUTE = 60
    MAX_AUTH_ATTEMPTS_PER_HOUR = 5
    MAX_WITHDRAW_REQUESTS_PER_DAY = 3
    MAX_SUPPORT_REQUESTS_PER_HOUR = 5
    
    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # Cache TTL (seconds)
    CACHE_TTL_SHORT = 60  # 1 minute
    CACHE_TTL_MEDIUM = 300  # 5 minutes
    CACHE_TTL_LONG = 3600  # 1 hour
    CACHE_TTL_DAY = 86400  # 24 hours
    
    # Token expiry
    JWT_EXPIRY_DAYS = 7
    REFRESH_TOKEN_EXPIRY_DAYS = 30
    API_KEY_EXPIRY_DAYS = 365
    
    # Notification
    FCM_BATCH_SIZE = 500
    MAX_NOTIFICATION_RETRIES = 3
    
    # File upload
    MAX_UPLOAD_SIZE_MB = 5
    ALLOWED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "webp"]
    ALLOWED_DOCUMENT_EXTENSIONS = ["pdf", "doc", "docx", "txt"]
    
    # Network
    ALLOWED_NETWORK_TYPES = ["mobile", "wifi", "ethernet"]
    BLOCKED_NETWORK_TYPES = ["vpn", "proxy", "tor"]
    
    # Regions (US + EU)
    ALLOWED_REGIONS = [
        "US",  # United States
        # EU Countries
        "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR",
        "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL",
        "PL", "PT", "RO", "SK", "SI", "ES", "SE"
    ]
    
    # VPN/Proxy detection
    VPN_SCORE_BLOCK_THRESHOLD = 70
    VPN_SCORE_WARN_THRESHOLD = 50
    MAX_VPN_SCORE = 100
    
    # Pricing
    DEFAULT_PRICE_PER_GB = 1.50
    DEFAULT_PRICE_PER_MB = 0.0015
    MIN_PRICE_PER_GB = 0.10
    MAX_PRICE_PER_GB = 10.00
    
    # Database
    DB_POOL_SIZE = 20
    DB_MAX_OVERFLOW = 10
    DB_POOL_TIMEOUT = 30
    
    # Logging
    LOG_RETENTION_DAYS = 30
    LOG_MAX_SIZE_MB = 100
    
    # Admin
    MAX_ADMIN_USERS = 10


class SessionStatus(str, Enum):
    """Session status enum"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TransactionType(str, Enum):
    """Transaction type enum"""
    INCOME = "income"
    WITHDRAW = "withdraw"
    REFUND = "refund"
    BONUS = "bonus"
    PENALTY = "penalty"


class TransactionStatus(str, Enum):
    """Transaction status enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WithdrawStatus(str, Enum):
    """Withdraw status enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationType(str, Enum):
    """Notification type enum"""
    BALANCE_UPDATED = "balance_updated"
    WITHDRAW_STATUS = "withdraw_status"
    SESSION_COMPLETED = "session_completed"
    SESSION_STARTED = "session_started"
    DAILY_PRICE = "daily_price"
    SYSTEM_UPDATE = "system_update"
    PROMO_CODE = "promo_code"
    SUPPORT_REPLY = "support_reply"


class SupportStatus(str, Enum):
    """Support request status enum"""
    NEW = "new"
    READ = "read"
    REPLIED = "replied"
    CLOSED = "closed"


class FilterStatus(str, Enum):
    """Filter status enum"""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class NetworkType(str, Enum):
    """Network type enum"""
    MOBILE = "mobile"
    WIFI = "wifi"
    ETHERNET = "ethernet"
    VPN = "vpn"
    PROXY = "proxy"
    UNKNOWN = "unknown"


class UserRole(str, Enum):
    """User role enum"""
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class ErrorCodes:
    """Error codes"""
    # Authentication errors
    INVALID_CREDENTIALS = "AUTH_001"
    TOKEN_EXPIRED = "AUTH_002"
    TOKEN_INVALID = "AUTH_003"
    UNAUTHORIZED = "AUTH_004"
    
    # Validation errors
    INVALID_INPUT = "VAL_001"
    MISSING_FIELD = "VAL_002"
    INVALID_FORMAT = "VAL_003"
    
    # Resource errors
    NOT_FOUND = "RES_001"
    ALREADY_EXISTS = "RES_002"
    CONFLICT = "RES_003"
    
    # Business logic errors
    INSUFFICIENT_BALANCE = "BUS_001"
    LIMIT_EXCEEDED = "BUS_002"
    OPERATION_NOT_ALLOWED = "BUS_003"
    
    # Network errors
    VPN_DETECTED = "NET_001"
    PROXY_DETECTED = "NET_002"
    REGION_NOT_ALLOWED = "NET_003"
    INVALID_NETWORK_TYPE = "NET_004"
    
    # System errors
    INTERNAL_ERROR = "SYS_001"
    SERVICE_UNAVAILABLE = "SYS_002"
    MAINTENANCE = "SYS_003"
