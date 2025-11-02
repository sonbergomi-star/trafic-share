package com.trafficsharing.app.data.model

import com.google.gson.annotations.SerializedName

// Auth Models
data class TelegramAuthRequest(
    val id: Long,
    val username: String? = null,
    val first_name: String? = null,
    val last_name: String? = null,
    val photo_url: String? = null,
    val auth_date: Long,
    val hash: String
)

data class AuthResponse(
    val status: String,
    val user: User? = null,
    val token: String? = null,
    val message: String? = null
)

data class User(
    val telegram_id: String,
    val username: String,
    val first_name: String,
    val photo_url: String,
    val balance_usd: Double,
    val auth_date: String?
)

// Dashboard Models
data class DashboardResponse(
    val user: User,
    val balance: BalanceInfo,
    val traffic: TrafficInfo,
    val pricing: PricingInfo,
    val mini_stats: MiniStats
)

data class BalanceInfo(
    val usd: Double,
    val converted_usdt: Double,
    val converted_uzs: Double
)

data class TrafficInfo(
    val sent_mb: Double,
    val used_mb: Double,
    val remaining_mb: Double
)

data class PricingInfo(
    val price_per_gb: Double,
    val date: String
)

data class MiniStats(
    val today_earn: Double,
    val week_earn: Double
)

// Traffic Models
data class TrafficStartRequest(
    val device_id: String? = null,
    val client_local_ip: String? = null,
    val network_type: String = "unknown",
    val app_version: String? = null,
    val os: String? = null,
    val battery_level: Int? = null
)

data class TrafficStartResponse(
    val status: String,
    val session_id: Long,
    val bypass: Boolean? = null,
    val message: String
)

data class TrafficReportRequest(
    val session_id: Long,
    val device_id: String,
    val cumulative_mb: Double,
    val delta_mb: Double,
    val speed: Double? = null,
    val battery_level: Int? = null,
    val network_type: String? = null,
    val timestamp: String? = null
)

// Balance Models
data class BalanceResponse(
    val user: User,
    val balance: BalanceDetail,
    val today_earn: Double,
    val month_earn: Double,
    val transactions: List<Transaction>
)

data class BalanceDetail(
    val usd: Double,
    val usdt_equivalent: Double,
    val sent_mb: Double,
    val used_mb: Double,
    val pending_usd: Double,
    val last_refreshed: String
)

data class Transaction(
    val id: Long,
    val type: String,
    val amount_usd: Double,
    val status: String,
    val created_at: String?
)

data class BalanceRefreshResponse(
    val status: String,
    val new_balance_usd: Double,
    val delta: Double
)

// Daily Price
data class DailyPriceResponse(
    val date: String?,
    val price_per_gb: Double,
    val message: String
)

// Withdraw Models
data class WithdrawRequest(
    val amount_usd: Double,
    val wallet_address: String,
    val network: String = "BEP20",
    val idempotency_key: String? = null
)

data class WithdrawResponse(
    val status: String,
    val withdraw_id: Long,
    val message: String
)

data class WithdrawHistoryItem(
    val id: Long,
    val amount_usd: Double,
    val wallet_address: String,
    val status: String,
    val tx_hash: String?,
    val created_at: String?
)

// Statistics Models
data class DailyStatsResponse(
    val date: String,
    val sent_mb: Double,
    val used_mb: Double,
    val profit_usd: Double,
    val price_per_mb: Double
)

data class WeeklyStatsResponse(
    val period: String,
    val sent_mb: Double,
    val used_mb: Double,
    val profit_usd: Double,
    val sessions_count: Int
)

data class MonthlyStatsResponse(
    val period: String,
    val sent_mb: Double,
    val used_mb: Double,
    val profit_usd: Double,
    val sessions_count: Int
)

// Session Models
data class SessionResponse(
    val id: Long,
    val start_time: String?,
    val end_time: String?,
    val duration: String?,
    val sent_mb: Double,
    val used_mb: Double,
    val earned_usd: Double,
    val status: String,
    val ip_address: String?,
    val location: String?,
    val device: String?
)

data class SessionSummaryResponse(
    val today: SessionPeriod,
    val week: SessionPeriod,
    val average_per_session: Double
)

data class SessionPeriod(
    val sessions: Int,
    val mb: Double,
    val earnings: Double
)

// Support Models
data class SupportRequest(
    val subject: String,
    val message: String,
    val attachment_url: String? = null
)

data class SupportResponse(
    val status: String,
    val message: String,
    val request_id: Long
)

data class SupportHistoryItem(
    val id: Long,
    val subject: String,
    val message: String,
    val status: String,
    val created_at: String?
)

// News & Promo Models
data class NewsPromoResponse(
    val telegram_links: TelegramLinks,
    val announcements: List<Announcement>,
    val promo: List<PromoCode>
)

data class TelegramLinks(
    val channel: String,
    val chat: String
)

data class Announcement(
    val id: Long,
    val title: String,
    val description: String?,
    val image_url: String?,
    val link: String?,
    val created_at: String?
)

data class PromoCode(
    val code: String,
    val bonus_percent: Double,
    val expires_at: String?,
    val is_active: Boolean
)

data class PromoActivateResponse(
    val status: String,
    val message: String
)

// Profile Models
data class ProfileResponse(
    val telegram_id: Long,
    val username: String?,
    val first_name: String?,
    val photo_url: String?,
    val auth_date: String?,
    val jwt_token: String?,
    val two_factor_enabled: Boolean,
    val last_login_ip: String?,
    val last_login_device: String?
)

data class TokenRenewResponse(
    val message: String,
    val jwt_token: String
)

// Settings Models
data class SettingsResponse(
    val language: String,
    val push_notifications: Boolean,
    val session_updates: Boolean,
    val system_updates: Boolean,
    val two_factor_enabled: Boolean,
    val single_device_mode: Boolean,
    val battery_saver: Boolean,
    val theme: String
)

data class SettingsUpdateRequest(
    val language: String? = null,
    val push_notifications: Boolean? = null,
    val session_updates: Boolean? = null,
    val system_updates: Boolean? = null,
    val two_factor_enabled: Boolean? = null,
    val single_device_mode: Boolean? = null,
    val battery_saver: Boolean? = null,
    val theme: String? = null
)

data class SettingsUpdateResponse(
    val status: String
)

// Base Response
data class BaseResponse(
    val status: String,
    val message: String? = null
)
