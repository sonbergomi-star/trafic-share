package com.traffic.platform.data.remote

import com.traffic.platform.data.remote.dto.AnalyticsResponse
import com.traffic.platform.data.remote.dto.AuthRequest
import com.traffic.platform.data.remote.dto.AuthResponse
import com.traffic.platform.data.remote.dto.BalanceRefreshRequest
import com.traffic.platform.data.remote.dto.BalanceResponse
import com.traffic.platform.data.remote.dto.DashboardResponse
import com.traffic.platform.data.remote.dto.GenericMessageResponse
import com.traffic.platform.data.remote.dto.NewsPromoResponse
import com.traffic.platform.data.remote.dto.SessionReportRequest
import com.traffic.platform.data.remote.dto.SessionStartRequest
import com.traffic.platform.data.remote.dto.SessionStopRequest
import com.traffic.platform.data.remote.dto.SettingsUpdateRequest
import com.traffic.platform.data.remote.dto.SupportCreateRequest
import com.traffic.platform.data.remote.dto.TransactionListResponse
import com.traffic.platform.data.remote.dto.WithdrawCreateRequest
import com.traffic.platform.data.remote.dto.WithdrawListResponse
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

interface TrafficApi {

    @POST("/api/auth/telegram")
    suspend fun loginWithTelegram(@Body body: AuthRequest): AuthResponse

    @GET("/api/dashboard/{telegramId}")
    suspend fun getDashboard(@Path("telegramId") telegramId: Long): DashboardResponse

    @POST("/api/traffic/start")
    suspend fun startTraffic(@Body body: SessionStartRequest): GenericMessageResponse

    @POST("/api/traffic/stop")
    suspend fun stopTraffic(@Body body: SessionStopRequest): GenericMessageResponse

    @POST("/api/traffic/report")
    suspend fun sendTrafficReport(@Body body: SessionReportRequest): GenericMessageResponse

    @GET("/api/user/balance/{telegramId}")
    suspend fun getBalance(@Path("telegramId") telegramId: Long): BalanceResponse

    @POST("/api/user/refresh_balance")
    suspend fun refreshBalance(@Body body: BalanceRefreshRequest): GenericMessageResponse

    @GET("/api/transactions")
    suspend fun getTransactions(): TransactionListResponse

    @POST("/api/withdraw")
    suspend fun createWithdraw(@Body body: WithdrawCreateRequest): GenericMessageResponse

    @GET("/api/withdraws")
    suspend fun getWithdraws(): WithdrawListResponse

    @GET("/api/stats/daily/{telegramId}")
    suspend fun getDailyAnalytics(@Path("telegramId") telegramId: Long): AnalyticsResponse

    @GET("/api/news_promo")
    suspend fun getNewsPromo(): NewsPromoResponse

    @POST("/api/user/settings")
    suspend fun updateSettings(@Body body: SettingsUpdateRequest): GenericMessageResponse

    @POST("/api/support/send")
    suspend fun sendSupport(@Body body: SupportCreateRequest): GenericMessageResponse
}
