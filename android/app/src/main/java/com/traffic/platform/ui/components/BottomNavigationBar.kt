package com.traffic.platform.ui.components

import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.navigation.NavController
import androidx.navigation.NavDestination.Companion.hierarchy
import com.traffic.platform.ui.navigation.Screen

@Composable
fun BottomNavigationBar(navController: NavController, currentRoute: String?) {
    NavigationBar {
        Screen.bottomBarItems.forEach { screen ->
            val selected = currentRoute == screen.route || navController.currentBackStackEntry?.destination?.hierarchy?.any { it.route == screen.route } == true
            NavigationBarItem(
                selected = selected,
                onClick = {
                    if (!selected) {
                        navController.navigate(screen.route) {
                            popUpTo(navController.graph.startDestinationId) {
                                saveState = true
                            }
                            launchSingleTop = true
                            restoreState = true
                        }
                    }
                },
                icon = { Icon(imageVector = screen.icon, contentDescription = screen.title) },
                label = { Text(screen.title) }
            )
        }
    }
}
