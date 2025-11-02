package com.traffic.platform

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import dagger.hilt.android.AndroidEntryPoint

import com.traffic.platform.ui.navigation.Screen
import com.traffic.platform.ui.screens.analytics.AnalyticsScreen
import com.traffic.platform.ui.screens.balance.BalanceScreen
import com.traffic.platform.ui.screens.dashboard.DashboardScreen
import com.traffic.platform.ui.screens.login.LoginScreen
import com.traffic.platform.ui.screens.news.NewsScreen
import com.traffic.platform.ui.screens.settings.SettingsScreen
import com.traffic.platform.ui.screens.support.SupportScreen
import com.traffic.platform.ui.theme.TrafficTheme
import com.traffic.platform.viewmodel.RootViewModel
import androidx.activity.viewModels
import com.traffic.platform.ui.components.BottomNavigationBar
import com.traffic.platform.ui.screens.traffic.TrafficScreen

@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    private val rootViewModel: RootViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            TrafficTheme {
                Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
                    AppHost(rootViewModel = rootViewModel)
                }
            }
        }
    }
}

@Composable
fun AppHost(rootViewModel: RootViewModel) {
    val navController = rememberNavController()
    val isAuthenticated by rootViewModel.isAuthenticated.collectAsState()
    val telegramId by rootViewModel.telegramId.collectAsState()

    val backStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = backStackEntry?.destination?.route

    Surface(modifier = Modifier.fillMaxSize()) {
        if (!isAuthenticated) {
            LoginScreen(onAuthenticated = { id -> rootViewModel.setAuthenticated(true, id) })
        } else {
            TrafficScaffold(
                navController = navController,
                currentRoute = currentRoute,
                content = {
                    NavHost(navController = navController, startDestination = Screen.Dashboard.route) {
                        composable(Screen.Dashboard.route) {
                            DashboardScreen(telegramId = telegramId ?: 0)
                        }
                        composable(Screen.Traffic.route) {
                            TrafficScreen()
                        }
                        composable(Screen.Balance.route) {
                            BalanceScreen(telegramId = telegramId ?: 0)
                        }
                        composable(Screen.Analytics.route) {
                            AnalyticsScreen(telegramId = telegramId ?: 0)
                        }
                        composable(Screen.News.route) {
                            NewsScreen()
                        }
                        composable(Screen.Settings.route) {
                            SettingsScreen(onLogout = {
                                rootViewModel.setAuthenticated(false, null)
                            })
                        }
                        composable(Screen.Support.route) {
                            SupportScreen(telegramId = telegramId ?: 0)
                        }
                    }
                }
            )
        }
    }
}

@Composable
fun TrafficScaffold(
    navController: androidx.navigation.NavHostController,
    currentRoute: String?,
    content: @Composable () -> Unit,
) {
    androidx.compose.material3.Scaffold(
        bottomBar = {
            BottomNavigationBar(navController = navController, currentRoute = currentRoute)
        }
    ) { innerPadding ->
        androidx.compose.foundation.layout.Box(modifier = Modifier
            .fillMaxSize()
            .padding(innerPadding)) {
            content()
        }
    }
}
