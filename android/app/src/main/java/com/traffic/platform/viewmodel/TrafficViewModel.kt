package com.traffic.platform.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.traffic.platform.data.remote.dto.GenericMessageResponse
import com.traffic.platform.data.remote.dto.SessionReportRequest
import com.traffic.platform.data.remote.dto.SessionStartRequest
import com.traffic.platform.data.remote.dto.SessionStopRequest
import com.traffic.platform.data.repository.TrafficRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class TrafficUiState(
    val sessionId: String? = null,
    val isActive: Boolean = false,
    val message: String? = null,
    val error: String? = null,
)

@HiltViewModel
class TrafficViewModel @Inject constructor(
    private val repository: TrafficRepository,
) : ViewModel() {

    private val _state = MutableStateFlow(TrafficUiState())
    val state: StateFlow<TrafficUiState> = _state

    fun startSession(request: SessionStartRequest) {
        viewModelScope.launch {
            runCatching { repository.startTraffic(request) }
                .onSuccess { response ->
                    _state.value = TrafficUiState(
                        sessionId = response.sessionId,
                        isActive = response.status == "ok",
                        message = response.message,
                    )
                }
                .onFailure { throwable ->
                    _state.value = _state.value.copy(error = throwable.message)
                }
        }
    }

    fun stopSession() {
        val id = _state.value.sessionId ?: return
        viewModelScope.launch {
            runCatching { repository.stopTraffic(SessionStopRequest(sessionId = id)) }
                .onSuccess { response ->
                    _state.value = TrafficUiState(
                        sessionId = null,
                        isActive = false,
                        message = response.message,
                    )
                }
                .onFailure { throwable ->
                    _state.value = _state.value.copy(error = throwable.message)
                }
        }
    }

    fun reportTelemetry(request: SessionReportRequest) {
        viewModelScope.launch {
            runCatching { repository.reportTraffic(request) }
        }
    }
}
