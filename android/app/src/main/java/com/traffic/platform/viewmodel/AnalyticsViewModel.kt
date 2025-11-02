package com.traffic.platform.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.traffic.platform.data.remote.dto.AnalyticsResponse
import com.traffic.platform.data.repository.TrafficRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class AnalyticsUiState(
    val isLoading: Boolean = true,
    val data: AnalyticsResponse? = null,
    val error: String? = null,
)

@HiltViewModel
class AnalyticsViewModel @Inject constructor(
    private val repository: TrafficRepository,
) : ViewModel() {

    private val _state = MutableStateFlow(AnalyticsUiState())
    val state: StateFlow<AnalyticsUiState> = _state

    fun load(telegramId: Long) {
        viewModelScope.launch {
            _state.value = _state.value.copy(isLoading = true, error = null)
            runCatching { repository.analytics(telegramId) }
                .onSuccess { response ->
                    _state.value = AnalyticsUiState(isLoading = false, data = response)
                }
                .onFailure { throwable ->
                    _state.value = AnalyticsUiState(isLoading = false, error = throwable.message)
                }
        }
    }
}
