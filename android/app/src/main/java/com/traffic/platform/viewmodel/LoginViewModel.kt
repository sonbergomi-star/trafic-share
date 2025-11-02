package com.traffic.platform.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.traffic.platform.data.remote.dto.AuthRequest
import com.traffic.platform.data.remote.dto.AuthResponse
import com.traffic.platform.data.repository.TrafficRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class LoginUiState(
    val isLoading: Boolean = false,
    val data: AuthResponse? = null,
    val error: String? = null,
)

@HiltViewModel
class LoginViewModel @Inject constructor(
    private val repository: TrafficRepository,
) : ViewModel() {

    private val _state = MutableStateFlow(LoginUiState())
    val state: StateFlow<LoginUiState> = _state

    fun loginWithTelegram(telegramId: Long, username: String?) {
        viewModelScope.launch {
            _state.value = LoginUiState(isLoading = true)
            val request = AuthRequest(
                id = telegramId,
                authDate = System.currentTimeMillis() / 1000,
                username = username,
                hash = "demo-hash",
            )

            runCatching { repository.login(request) }
                .onSuccess { response ->
                    _state.value = LoginUiState(isLoading = false, data = response)
                }
                .onFailure { throwable ->
                    _state.value = LoginUiState(isLoading = false, error = throwable.message)
                }
        }
    }
}
