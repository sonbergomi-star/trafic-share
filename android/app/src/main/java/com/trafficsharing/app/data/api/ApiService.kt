package com.trafficsharing.app.data.api

import com.trafficsharing.app.data.model.*
import retrofit2.Response
import retrofit2.http.*

interface ApiService {
    
    // Auth
    @POST("auth/telegram")
    suspend fun authenticateTelegram(@Body request: TelegramAuthRequest): Response<AuthResponse>
    
    // Dashboard
    @GET("dashboard/{telegram_id}")
    suspend fun getDashboard(@Path("telegram_id") telegramId: Long): Response<DashboardResponse>
    
    // Traffic
    @POST("traffic/start")
    suspend fun startTraffic(@Body request: TrafficStartRequest): Response<TrafficStartResponse>
    
    @POST("traffic/stop")
    suspend fun stopTraffic(@Query("session_id") sessionId: Long): Response<BaseResponse>
    
    @POST("traffic/report")
    suspend fun reportTraffic(@Body request: TrafficReportRequest): Response<BaseResponse>
    
    // Balance
    @GET("user/balance/{telegram_id}")
    suspend fun getBalance(@Path("telegram_id") telegramId: Long): Response<BalanceResponse>
    
    @POST("user/refresh_balance")
    suspend fun refreshBalance(@Query("telegram_id") telegramId: Long): Response<BalanceRefreshResponse>
    
    // Daily Price
    @GET("daily_price")
    suspend fun getDailyPrice(): Response<DailyPriceResponse>
    
    // Withdraw
    @POST("withdraw")
    suspend fun createWithdraw(@Body request: WithdrawRequest): Response<WithdrawResponse>
    
    @GET("withdraw")
    suspend fun getWithdraws(): Response<List<WithdrawHistoryItem>>
    
    // Statistics
    @GET("stats/daily/{telegram_id}")
    suspend fun getDailyStats(@Path("telegram_id") telegramId: Long): Response<DailyStatsResponse>
    
    @GET("stats/weekly/{telegram_id}")
    suspend fun getWeeklyStats(@Path("telegram_id") telegramId: Long): Response<WeeklyStatsResponse>
    
    @GET("stats/monthly/{telegram_id}")
    suspend fun getMonthlyStats(@Path("telegram_id") telegramId: Long): Response<MonthlyStatsResponse>
    
    // Sessions
    @GET("sessions")
    suspend fun getSessions(
        @Query("limit") limit: Int = 20,
        @Query("offset") offset: Int = 0
    ): Response<List<SessionResponse>>
    
    @GET("sessions/{session_id}")
    suspend fun getSession(@Path("session_id") sessionId: Long): Response<SessionResponse>
    
    @GET("sessions/summary")
    suspend fun getSessionSummary(): Response<SessionSummaryResponse>
    
    // Support
    @POST("support/send")
    suspend fun sendSupport(@Body request: SupportRequest): Response<SupportResponse>
    
    @GET("support/history")
    suspend fun getSupportHistory(): Response<List<SupportHistoryItem>>
    
    // News & Promo
    @GET("news/promo")
    suspend fun getNewsPromo(): Response<NewsPromoResponse>
    
    @POST("news/promo/activate")
    suspend fun activatePromo(@Query("code") code: String): Response<PromoActivateResponse>
    
    // Profile
    @GET("profile")
    suspend fun getProfile(): Response<ProfileResponse>
    
    @POST("profile/token/renew")
    suspend fun renewToken(): Response<TokenRenewResponse>
    
    @POST("profile/logout")
    suspend fun logout(): Response<BaseResponse>
    
    // Settings
    @GET("settings/settings")
    suspend fun getSettings(): Response<SettingsResponse>
    
    @PATCH("settings/settings")
    suspend fun updateSettings(@Body request: SettingsUpdateRequest): Response<SettingsUpdateResponse>
    
    @POST("settings/logout_all")
    suspend fun logoutAll(): Response<BaseResponse>
}
