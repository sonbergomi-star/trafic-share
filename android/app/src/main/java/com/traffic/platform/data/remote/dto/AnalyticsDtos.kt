package com.traffic.platform.data.remote.dto

import kotlinx.serialization.Serializable

@Serializable
data class AnalyticsItemDto(
    val date: String,
    val sent_mb: Double,
    val sold_mb: Double,
    val profit_usd: Double,
    val price_per_mb: Double,
)

@Serializable
data class AnalyticsResponse(
    val items: List<AnalyticsItemDto>,
)
