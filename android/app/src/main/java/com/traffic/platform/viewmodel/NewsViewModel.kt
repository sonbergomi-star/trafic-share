package com.traffic.platform.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.traffic.platform.data.remote.dto.NewsPromoResponse
import com.traffic.platform.data.repository.TrafficRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class NewsUiState(
    val isLoading: Boolean = true,
    val data: NewsPromoResponse? = null,
    val error: String? = null,
)

@HiltViewModel
class NewsViewModel @Inject constructor(
    private val repository: TrafficRepository,
) : ViewModel() {

    private val _state = MutableStateFlow(NewsUiState())
    val state: StateFlow<NewsUiState> = _state

    fun load() {
        viewModelScope.launch {
            _state.value = _state.value.copy(isLoading = true, error = null)
            runCatching { repository.newsPromo() }
                .onSuccess { response ->
                    _state.value = NewsUiState(isLoading = false, data = response)
                }
                .onFailure { throwable ->
                    _state.value = NewsUiState(isLoading = false, error = throwable.message)
                }
        }
    }
}
