package com.traffic.platform.data.remote.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class TransactionDto(
    val id: Long,
    val type: String,
    @SerialName("amount_usd") val amountUsd: Double,
    val status: String,
    @SerialName("created_at") val createdAt: String,
    val note: String? = null,
)

@Serializable
data class TransactionListResponse(
    val items: List<TransactionDto>,
    val total: Int,
)

@Serializable
data class WithdrawCreateRequest(
    @SerialName("telegram_id") val telegramId: Long,
    @SerialName("amount_usd") val amountUsd: Double,
    @SerialName("wallet_address") val walletAddress: String,
    val network: String = "BEP20",
    @SerialName("idempotency_key") val idempotencyKey: String? = null,
)

@Serializable
data class WithdrawItemDto(
    val id: Long,
    @SerialName("amount_usd") val amountUsd: Double,
    val status: String,
    @SerialName("created_at") val createdAt: String,
    @SerialName("processed_at") val processedAt: String? = null,
    @SerialName("tx_hash") val txHash: String? = null,
)

@Serializable
data class WithdrawListResponse(
    val items: List<WithdrawItemDto>,
    val total: Int,
)
