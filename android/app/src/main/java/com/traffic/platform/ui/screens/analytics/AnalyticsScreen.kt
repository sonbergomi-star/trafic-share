package com.traffic.platform.ui.screens.analytics

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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
import com.traffic.platform.viewmodel.AnalyticsViewModel

@Composable
fun AnalyticsScreen(telegramId: Long, viewModel: AnalyticsViewModel = hiltViewModel()) {
    LaunchedEffect(telegramId) {
        if (telegramId != 0L) {
            viewModel.load(telegramId)
        }
    }

    val state by viewModel.state.collectAsState()

    when {
        state.isLoading -> {
            Column(
                modifier = Modifier.fillMaxSize(),
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                CircularProgressIndicator(modifier = Modifier.padding(top = 32.dp))
            }
        }
        state.error != null -> {
            Text(state.error ?: "Error", color = MaterialTheme.colorScheme.error, modifier = Modifier.padding(16.dp))
        }
        state.data != null -> {
            LazyColumn(modifier = Modifier.fillMaxSize().padding(16.dp)) {
                items(state.data!!.items) { item ->
                    Card(modifier = Modifier.padding(bottom = 12.dp)) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text(item.date, style = MaterialTheme.typography.titleMedium)
                            Text("Sent: ${item.sent_mb} MB")
                            Text("Sold: ${item.sold_mb} MB")
                            Text("Profit: ${item.profit_usd} USD")
                        }
                    }
                }
            }
        }
    }
}
