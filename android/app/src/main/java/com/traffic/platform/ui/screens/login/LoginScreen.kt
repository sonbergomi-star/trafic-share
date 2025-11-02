package com.traffic.platform.ui.screens.login

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.traffic.platform.viewmodel.LoginViewModel

@Composable
fun LoginScreen(
    modifier: Modifier = Modifier,
    onAuthenticated: (Long) -> Unit,
    viewModel: LoginViewModel = hiltViewModel(),
) {
    val state = viewModel.state
    val snackbarHost = remember { SnackbarHostState() }

    LaunchedEffect(state.value.data) {
        val auth = state.value.data
        if (auth != null) {
            onAuthenticated(auth.user.telegramId)
        }
    }

    LaunchedEffect(state.value.error) {
        state.value.error?.let { snackbarHost.showSnackbar(it) }
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(
            text = "Traffic Platform",
            style = MaterialTheme.typography.headlineMedium,
        )
        Text(
            text = "Login with Telegram to continue",
            style = MaterialTheme.typography.bodyMedium,
            modifier = Modifier.padding(top = 8.dp, bottom = 24.dp)
        )

        if (state.value.isLoading) {
            CircularProgressIndicator()
        } else {
            Button(
                onClick = {
                    viewModel.loginWithTelegram(
                        telegramId = 999999999L,
                        username = "demo_user",
                    )
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(text = "Login with Telegram")
            }
        }

        SnackbarHost(hostState = snackbarHost)
    }
}
