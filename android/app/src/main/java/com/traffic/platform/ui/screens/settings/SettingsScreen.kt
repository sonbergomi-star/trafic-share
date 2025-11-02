package com.traffic.platform.ui.screens.settings

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.traffic.platform.data.remote.dto.SettingsUpdateRequest
import com.traffic.platform.viewmodel.SettingsViewModel

@Composable
fun SettingsScreen(onLogout: () -> Unit, viewModel: SettingsViewModel = hiltViewModel()) {
    val pushEnabled = remember { mutableStateOf(true) }
    val sessionUpdates = remember { mutableStateOf(true) }
    val systemUpdates = remember { mutableStateOf(true) }
    val darkTheme = remember { mutableStateOf(false) }

    val state by viewModel.state.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Text("Settings", style = MaterialTheme.typography.headlineSmall)

        SettingsToggle(title = "Push Notifications", checked = pushEnabled.value) {
            pushEnabled.value = it
        }
        SettingsToggle(title = "Session Updates", checked = sessionUpdates.value) {
            sessionUpdates.value = it
        }
        SettingsToggle(title = "System Updates", checked = systemUpdates.value) {
            systemUpdates.value = it
        }
        SettingsToggle(title = "Dark Theme", checked = darkTheme.value) {
            darkTheme.value = it
        }

        Button(onClick = {
            viewModel.updateSettings(
                SettingsUpdateRequest(
                    pushNotifications = pushEnabled.value,
                    sessionUpdates = sessionUpdates.value,
                    systemUpdates = systemUpdates.value,
                    theme = if (darkTheme.value) "dark" else "light",
                )
            )
        }, modifier = Modifier.fillMaxWidth()) {
            if (state.isSaving) {
                CircularProgressIndicator(modifier = Modifier.padding(end = 8.dp))
            }
            Text("Save Settings")
        }

        Button(onClick = onLogout, modifier = Modifier.fillMaxWidth()) {
            Text("Logout")
        }

        state.successMessage?.let {
            Text(text = it, color = MaterialTheme.colorScheme.primary)
        }
        state.error?.let {
            Text(text = it, color = MaterialTheme.colorScheme.error)
        }
    }
}

@Composable
private fun SettingsToggle(title: String, checked: Boolean, onCheckedChange: (Boolean) -> Unit) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceBetween,
    ) {
        Text(title)
        Switch(checked = checked, onCheckedChange = onCheckedChange)
    }
}
