package com.traffic.platform.ui.screens.support

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.traffic.platform.data.remote.dto.SupportCreateRequest
import com.traffic.platform.viewmodel.SupportViewModel

@Composable
fun SupportScreen(telegramId: Long, viewModel: SupportViewModel = hiltViewModel()) {
    val subject = remember { mutableStateOf("") }
    val message = remember { mutableStateOf("") }

    val state by viewModel.state.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text("Support", modifier = Modifier.padding(bottom = 16.dp))
        OutlinedTextField(
            value = subject.value,
            onValueChange = { subject.value = it },
            label = { Text("Subject") },
            modifier = Modifier.fillMaxWidth(),
        )
        OutlinedTextField(
            value = message.value,
            onValueChange = { message.value = it },
            label = { Text("Message") },
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 12.dp),
            minLines = 3,
        )

        Button(
            onClick = {
                viewModel.submit(
                    SupportCreateRequest(
                        telegramId = telegramId,
                        subject = subject.value,
                        message = message.value,
                    )
                )
            },
            enabled = !state.isSubmitting,
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 16.dp)
        ) {
            Text(if (state.isSubmitting) "Sending..." else "Send")
        }

        if (state.success) {
            Text("Support request sent successfully!", modifier = Modifier.padding(top = 12.dp))
        }

        state.error?.let {
            Text(it, color = androidx.compose.material3.MaterialTheme.colorScheme.error, modifier = Modifier.padding(top = 12.dp))
        }
    }
}
