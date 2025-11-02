package com.traffic.platform.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.traffic.platform.data.remote.dto.DashboardResponse
import com.traffic.platform.data.repository.TrafficRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class DashboardUiState(
    val isLoading: Boolean = true,
    val data: DashboardResponse? = null,
    val error: String? = null,
)

@HiltViewModel
class DashboardViewModel @Inject constructor(
    private val repository: TrafficRepository,
) : ViewModel() {

    private val _state = MutableStateFlow(DashboardUiState())
    val state: StateFlow<DashboardUiState> = _state

    fun loadDashboard(telegramId: Long) {
        _state.value = _state.value.copy(isLoading = true, error = null)
        viewModelScope.launch {
            runCatching { repository.dashboard(telegramId) }
                .onSuccess { data ->
                    _state.value = DashboardUiState(isLoading = false, data = data)
                }
                .onFailure { throwable ->
                    _state.value = DashboardUiState(isLoading = false, error = throwable.message)
                }
        }
    }
}
