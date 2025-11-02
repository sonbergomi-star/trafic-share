package com.traffic.platform.ui.screens.balance

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
import com.traffic.platform.viewmodel.BalanceViewModel

@Composable
fun BalanceScreen(
    telegramId: Long,
    viewModel: BalanceViewModel = hiltViewModel(),
) {
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
            Text(
                text = state.error ?: "Unknown error",
                modifier = Modifier.padding(16.dp),
                color = MaterialTheme.colorScheme.error,
            )
        }
        state.balance != null -> {
            val balance = state.balance
            val transactions = state.transactions?.items.orEmpty()
            LazyColumn(modifier = Modifier.fillMaxSize().padding(16.dp)) {
                item {
                    Card(modifier = Modifier.padding(bottom = 16.dp)) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text("Current Balance", style = MaterialTheme.typography.titleMedium)
                            Text("${balance.balance.usd} USD", style = MaterialTheme.typography.headlineMedium)
                            Text("Today: ${balance.todayEarn} USD")
                            Text("Month: ${balance.monthEarn} USD")
                        }
                    }
                }
                items(transactions) { tx ->
                    Card(modifier = Modifier.padding(bottom = 12.dp)) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text("${tx.type.uppercase()} ? ${tx.status}", style = MaterialTheme.typography.titleSmall)
                            Text("Amount: ${tx.amountUsd} USD")
                            Text("Date: ${tx.createdAt}")
                            tx.note?.let { Text(it, style = MaterialTheme.typography.bodySmall) }
                        }
                    }
                }
            }
        }
    }
}
