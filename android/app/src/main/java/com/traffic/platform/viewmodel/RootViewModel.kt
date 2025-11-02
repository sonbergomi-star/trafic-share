package com.traffic.platform.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class RootViewModel @Inject constructor() : ViewModel() {

    private val _isAuthenticated = MutableStateFlow(false)
    val isAuthenticated: StateFlow<Boolean> = _isAuthenticated

    private val _telegramId = MutableStateFlow<Long?>(null)
    val telegramId: StateFlow<Long?> = _telegramId

    fun setAuthenticated(value: Boolean, telegramId: Long? = null) {
        viewModelScope.launch {
            _isAuthenticated.emit(value)
            _telegramId.emit(telegramId)
        }
    }
}
