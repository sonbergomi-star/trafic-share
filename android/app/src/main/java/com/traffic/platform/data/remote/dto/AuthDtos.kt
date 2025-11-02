package com.traffic.platform.data.remote.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class AuthRequest(
    val id: Long,
    @SerialName("first_name") val firstName: String? = null,
    val username: String? = null,
    @SerialName("photo_url") val photoUrl: String? = null,
    @SerialName("auth_date") val authDate: Long,
    val hash: String,
)

@Serializable
data class TokenDto(
    @SerialName("access_token") val accessToken: String,
    @SerialName("refresh_token") val refreshToken: String,
    @SerialName("token_type") val tokenType: String,
)

@Serializable
data class AuthResponse(
    val status: String,
    val user: UserDto,
    val token: TokenDto,
)

@Serializable
data class UserDto(
    @SerialName("telegram_id") val telegramId: Long,
    val username: String? = null,
    @SerialName("first_name") val firstName: String? = null,
    @SerialName("photo_url") val photoUrl: String? = null,
    @SerialName("balance_usd") val balanceUsd: Double = 0.0,
)
