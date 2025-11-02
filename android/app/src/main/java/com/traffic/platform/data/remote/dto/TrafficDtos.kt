package com.traffic.platform.data.remote.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class SessionStartRequest(
    @SerialName("device_id") val deviceId: String,
    @SerialName("client_local_ip") val clientLocalIp: String? = null,
    @SerialName("network_type") val networkType: String? = null,
    @SerialName("app_version") val appVersion: String? = null,
    val os: String? = null,
    @SerialName("battery_level") val batteryLevel: Int? = null,
)

@Serializable
data class SessionStopRequest(
    @SerialName("session_id") val sessionId: String,
)

@Serializable
data class SessionReportRequest(
    @SerialName("session_id") val sessionId: String,
    @SerialName("device_id") val deviceId: String,
    @SerialName("sequence_number") val sequenceNumber: Int,
    @SerialName("delta_mb") val deltaMb: Double,
    @SerialName("cumulative_mb") val cumulativeMb: Double,
    @SerialName("speed_mb_s") val speedMb: Double,
    @SerialName("battery_level") val batteryLevel: Int? = null,
    @SerialName("network_type") val networkType: String? = null,
    val timestamp: String,
    val extra: Map<String, String>? = null,
)

@Serializable
data class GenericMessageResponse(
    val status: String,
    val message: String? = null,
    @SerialName("session_id") val sessionId: String? = null,
)
