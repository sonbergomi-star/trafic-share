package com.traffic.platform.data.remote.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class DashboardResponse(
    val user: DashboardUserDto,
    val balance: DashboardBalanceDto,
    val traffic: DashboardTrafficDto,
    val pricing: DashboardPricingDto,
    @SerialName("mini_stats") val miniStats: DashboardMiniStatsDto,
    @SerialName("last_updated") val lastUpdated: String,
)

@Serializable
data class DashboardUserDto(
    @SerialName("telegram_id") val telegramId: Long,
    @SerialName("first_name") val firstName: String?,
    val username: String?,
    @SerialName("photo_url") val photoUrl: String?,
    @SerialName("auth_date") val authDate: String?,
)

@Serializable
data class DashboardBalanceDto(
    val usd: Double,
    @SerialName("converted_usdt") val convertedUsdt: Double,
    @SerialName("converted_uzs") val convertedUzs: Double? = null,
)

@Serializable
data class DashboardTrafficDto(
    @SerialName("sent_mb") val sentMb: Double,
    @SerialName("used_mb") val usedMb: Double,
    @SerialName("remaining_mb") val remainingMb: Double,
)

@Serializable
data class DashboardPricingDto(
    @SerialName("price_per_gb") val pricePerGb: Double,
    val message: String? = null,
    val change: Double? = null,
)

@Serializable
data class DashboardMiniStatsDto(
    @SerialName("today_earn") val todayEarn: Double,
    @SerialName("week_earn") val weekEarn: Double,
    @SerialName("month_earn") val monthEarn: Double,
    @SerialName("active_sessions_estimate") val activeSessionsEstimate: Double? = 0.0,
)
