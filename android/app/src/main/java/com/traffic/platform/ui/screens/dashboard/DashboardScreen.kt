package com.traffic.platform.ui.screens.dashboard

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.traffic.platform.viewmodel.DashboardViewModel

@Composable
fun DashboardScreen(
    telegramId: Long,
    viewModel: DashboardViewModel = hiltViewModel(),
) {
    LaunchedEffect(telegramId) {
        if (telegramId != 0L) {
            viewModel.loadDashboard(telegramId)
        }
    }

    val state by viewModel.state.collectAsState()

    when {
        state.isLoading -> {
            Column(
                modifier = Modifier.fillMaxSize(),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                CircularProgressIndicator()
            }
        }
        state.error != null -> {
            Text(
                text = state.error ?: "Unknown error",
                modifier = Modifier.padding(16.dp),
                color = MaterialTheme.colorScheme.error,
            )
        }
        state.data != null -> {
            val dashboard = state.data
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp),
            ) {
                Text(
                    text = "Salom, ${dashboard?.user?.firstName ?: dashboard?.user?.username}",
                    style = MaterialTheme.typography.headlineSmall,
                )

                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text("Balance", style = MaterialTheme.typography.titleMedium)
                        Text("${dashboard?.balance?.usd ?: 0.0} USD", style = MaterialTheme.typography.headlineMedium)
                        Text("USDT: ${dashboard?.balance?.convertedUsdt ?: 0.0}")
                    }
                }

                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text("Traffic", style = MaterialTheme.typography.titleMedium)
                        Text("Sent: ${dashboard?.traffic?.sentMb ?: 0.0} MB")
                        Text("Used: ${dashboard?.traffic?.usedMb ?: 0.0} MB")
                        Text("Remaining: ${dashboard?.traffic?.remainingMb ?: 0.0} MB")
                    }
                }

                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text("Today Earnings", style = MaterialTheme.typography.titleMedium)
                        Text("${dashboard?.miniStats?.todayEarn ?: 0.0} USD")
                        Spacer(modifier = Modifier.height(8.dp))
                        Text("Weekly: ${dashboard?.miniStats?.weekEarn ?: 0.0} USD")
                        Text("Monthly: ${dashboard?.miniStats?.monthEarn ?: 0.0} USD")
                    }
                }
            }
        }
    }
}
