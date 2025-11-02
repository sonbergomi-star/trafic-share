package com.traffic.platform.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.traffic.platform.data.remote.dto.SupportCreateRequest
import com.traffic.platform.data.repository.TrafficRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class SupportUiState(
    val isSubmitting: Boolean = false,
    val success: Boolean = false,
    val error: String? = null,
)

@HiltViewModel
class SupportViewModel @Inject constructor(
    private val repository: TrafficRepository,
) : ViewModel() {

    private val _state = MutableStateFlow(SupportUiState())
    val state: StateFlow<SupportUiState> = _state

    fun submit(request: SupportCreateRequest) {
        viewModelScope.launch {
            _state.value = SupportUiState(isSubmitting = true)
            runCatching { repository.sendSupport(request) }
                .onSuccess {
                    _state.value = SupportUiState(isSubmitting = false, success = true)
                }
                .onFailure { throwable ->
                    _state.value = SupportUiState(isSubmitting = false, error = throwable.message)
                }
        }
    }
}
