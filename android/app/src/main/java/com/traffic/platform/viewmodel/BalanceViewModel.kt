package com.traffic.platform.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.traffic.platform.data.remote.dto.BalanceRefreshRequest
import com.traffic.platform.data.remote.dto.BalanceResponse
import com.traffic.platform.data.remote.dto.TransactionListResponse
import com.traffic.platform.data.repository.TrafficRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class BalanceUiState(
    val isLoading: Boolean = true,
    val balance: BalanceResponse? = null,
    val transactions: TransactionListResponse? = null,
    val error: String? = null,
)

@HiltViewModel
class BalanceViewModel @Inject constructor(
    private val repository: TrafficRepository,
) : ViewModel() {

    private val _state = MutableStateFlow(BalanceUiState())
    val state: StateFlow<BalanceUiState> = _state

    fun load(telegramId: Long) {
        viewModelScope.launch {
            _state.value = _state.value.copy(isLoading = true, error = null)
            runCatching {
                val balance = repository.balance(telegramId)
                val transactions = repository.transactions()
                balance to transactions
            }.onSuccess { (balance, transactions) ->
                _state.value = BalanceUiState(
                    isLoading = false,
                    balance = balance,
                    transactions = transactions,
                )
            }.onFailure { throwable ->
                _state.value = BalanceUiState(isLoading = false, error = throwable.message)
            }
        }
    }

    fun refresh(telegramId: Long) {
        viewModelScope.launch {
            runCatching { repository.refreshBalance(BalanceRefreshRequest(telegramId)) }
            load(telegramId)
        }
    }
}
