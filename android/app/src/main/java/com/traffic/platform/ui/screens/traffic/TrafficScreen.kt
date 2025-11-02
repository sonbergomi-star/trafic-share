package com.traffic.platform.ui.screens.traffic

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.traffic.platform.data.remote.dto.SessionStartRequest
import com.traffic.platform.viewmodel.TrafficViewModel

@Composable
fun TrafficScreen(viewModel: TrafficViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center,
    ) {
        Text("Traffic Control", style = MaterialTheme.typography.headlineSmall)
        Text(
            text = state.message ?: "Session ${if (state.isActive) "Active" else "Idle"}",
            modifier = Modifier.padding(top = 8.dp, bottom = 24.dp)
        )

        if (!state.isActive) {
            Button(
                onClick = {
                    viewModel.startSession(
                        SessionStartRequest(
                            deviceId = "android-device",
                            networkType = "mobile",
                            os = "Android",
                            appVersion = "1.0.0",
                        )
                    )
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Start Sharing")
            }
        } else {
            Button(
                onClick = { viewModel.stopSession() },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Stop Session")
            }
        }

        state.error?.let {
            Text(text = it, color = MaterialTheme.colorScheme.error, modifier = Modifier.padding(top = 16.dp))
        }
    }
}
