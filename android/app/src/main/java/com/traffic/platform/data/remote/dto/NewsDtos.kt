package com.traffic.platform.data.remote.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class NewsPromoResponse(
    @SerialName("telegram_links") val telegramLinks: TelegramLinksDto,
    val announcements: List<AnnouncementDto>,
    val promo: List<PromoDto>,
)

@Serializable
data class TelegramLinksDto(
    val channel: String,
    val chat: String,
)

@Serializable
data class AnnouncementDto(
    val id: Long,
    val title: String,
    val description: String,
    @SerialName("image_url") val imageUrl: String? = null,
    val link: String? = null,
    @SerialName("created_at") val createdAt: String,
)

@Serializable
data class PromoDto(
    val code: String,
    @SerialName("bonus_percent") val bonusPercent: Double,
    @SerialName("expires_at") val expiresAt: String,
    @SerialName("is_active") val isActive: Boolean,
)
