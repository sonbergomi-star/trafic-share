package com.traffic.platform.data.remote.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class SupportCreateRequest(
    @SerialName("telegram_id") val telegramId: Long,
    val subject: String,
    val message: String,
    @SerialName("attachment_url") val attachmentUrl: String? = null,
)
