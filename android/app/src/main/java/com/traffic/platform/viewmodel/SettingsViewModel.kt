package com.traffic.platform.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.traffic.platform.data.remote.dto.SettingsUpdateRequest
import com.traffic.platform.data.repository.TrafficRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class SettingsUiState(
    val isSaving: Boolean = false,
    val successMessage: String? = null,
    val error: String? = null,
)

@HiltViewModel
class SettingsViewModel @Inject constructor(
    private val repository: TrafficRepository,
) : ViewModel() {

    private val _state = MutableStateFlow(SettingsUiState())
    val state: StateFlow<SettingsUiState> = _state

    fun updateSettings(request: SettingsUpdateRequest) {
        viewModelScope.launch {
            _state.value = SettingsUiState(isSaving = true)
            runCatching { repository.updateSettings(request) }
                .onSuccess { response ->
                    _state.value = SettingsUiState(
                        isSaving = false,
                        successMessage = response.message ?: "Settings updated",
                    )
                }
                .onFailure { throwable ->
                    _state.value = SettingsUiState(isSaving = false, error = throwable.message)
                }
        }
    }
}
