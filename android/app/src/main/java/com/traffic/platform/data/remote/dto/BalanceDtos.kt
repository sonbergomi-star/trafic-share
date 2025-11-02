package com.traffic.platform.data.remote.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class BalanceResponse(
    val user: DashboardUserDto,
    val balance: BalanceSnapshotDto,
    @SerialName("today_earn") val todayEarn: Double,
    @SerialName("month_earn") val monthEarn: Double,
    val transactions: List<TransactionDto>,
)

@Serializable
data class BalanceSnapshotDto(
    val usd: Double,
    @SerialName("sent_mb") val sentMb: Double,
    @SerialName("used_mb") val usedMb: Double,
    @SerialName("pending_usd") val pendingUsd: Double,
    @SerialName("last_refreshed") val lastRefreshed: String,
)

@Serializable
data class BalanceRefreshRequest(
    @SerialName("telegram_id") val telegramId: Long,
)
