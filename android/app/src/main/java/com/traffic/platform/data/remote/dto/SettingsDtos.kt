package com.traffic.platform.data.remote.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class SettingsUpdateRequest(
    val language: String? = null,
    @SerialName("push_notifications") val pushNotifications: Boolean? = null,
    @SerialName("session_updates") val sessionUpdates: Boolean? = null,
    @SerialName("system_updates") val systemUpdates: Boolean? = null,
    @SerialName("two_factor_enabled") val twoFactorEnabled: Boolean? = null,
    @SerialName("single_device_mode") val singleDeviceMode: Boolean? = null,
    @SerialName("battery_saver") val batterySaver: Boolean? = null,
    val theme: String? = null,
)
