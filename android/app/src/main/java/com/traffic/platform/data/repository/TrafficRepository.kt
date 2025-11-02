package com.traffic.platform.data.repository

import com.traffic.platform.data.remote.TrafficApi
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
import javax.inject.Inject

class TrafficRepository @Inject constructor(
    private val api: TrafficApi,
) {
    suspend fun login(payload: AuthRequest): AuthResponse = api.loginWithTelegram(payload)

    suspend fun dashboard(telegramId: Long): DashboardResponse = api.getDashboard(telegramId)

    suspend fun startTraffic(request: SessionStartRequest): GenericMessageResponse = api.startTraffic(request)

    suspend fun stopTraffic(request: SessionStopRequest): GenericMessageResponse = api.stopTraffic(request)

    suspend fun reportTraffic(request: SessionReportRequest): GenericMessageResponse = api.sendTrafficReport(request)

    suspend fun balance(telegramId: Long): BalanceResponse = api.getBalance(telegramId)

    suspend fun refreshBalance(request: BalanceRefreshRequest): GenericMessageResponse = api.refreshBalance(request)

    suspend fun transactions(): TransactionListResponse = api.getTransactions()

    suspend fun withdraw(request: WithdrawCreateRequest): GenericMessageResponse = api.createWithdraw(request)

    suspend fun withdraws(): WithdrawListResponse = api.getWithdraws()

    suspend fun analytics(telegramId: Long) = api.getDailyAnalytics(telegramId)

    suspend fun newsPromo(): NewsPromoResponse = api.getNewsPromo()

    suspend fun updateSettings(request: SettingsUpdateRequest): GenericMessageResponse = api.updateSettings(request)

    suspend fun sendSupport(request: SupportCreateRequest): GenericMessageResponse = api.sendSupport(request)
}
