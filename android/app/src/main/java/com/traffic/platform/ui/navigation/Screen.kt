package com.traffic.platform.ui.navigation

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Analytics
import androidx.compose.material.icons.outlined.Dashboard
import androidx.compose.material.icons.outlined.HelpOutline
import androidx.compose.material.icons.outlined.News
import androidx.compose.material.icons.outlined.Settings
import androidx.compose.material.icons.outlined.TrendingUp
import androidx.compose.material.icons.outlined.Wallet
import androidx.compose.ui.graphics.vector.ImageVector

sealed class Screen(val route: String, val title: String, val icon: ImageVector) {
    object Dashboard : Screen("dashboard", "Dashboard", Icons.Outlined.Dashboard)
    object Traffic : Screen("traffic", "Traffic", Icons.Outlined.TrendingUp)
    object Balance : Screen("balance", "Balance", Icons.Outlined.Wallet)
    object Analytics : Screen("analytics", "Analytics", Icons.Outlined.Analytics)
    object News : Screen("news", "News", Icons.Outlined.News)
    object Settings : Screen("settings", "Settings", Icons.Outlined.Settings)
    object Support : Screen("support", "Support", Icons.Outlined.HelpOutline)

    companion object {
        val bottomBarItems = listOf(Dashboard, Traffic, Balance, Analytics, News, Settings, Support)
    }
}
