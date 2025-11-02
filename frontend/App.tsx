import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Screens
import TelegramAuthScreen from './src/screens/TelegramAuthScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import BalanceScreen from './src/screens/BalanceScreen';
import WithdrawScreen from './src/screens/WithdrawScreen';
import StatisticsScreen from './src/screens/StatisticsScreen';
import SessionHistoryScreen from './src/screens/SessionHistoryScreen';
import SupportScreen from './src/screens/SupportScreen';
import NewsScreen from './src/screens/NewsScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import SettingsScreen from './src/screens/SettingsScreen';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: string;

          switch (route.name) {
            case 'Dashboard':
              iconName = 'view-dashboard';
              break;
            case 'Balance':
              iconName = 'wallet';
              break;
            case 'Statistics':
              iconName = 'chart-line';
              break;
            case 'Profile':
              iconName = 'account';
              break;
            default:
              iconName = 'circle';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#007bff',
        tabBarInactiveTintColor: 'gray',
      })}
    >
      <Tab.Screen 
        name="Dashboard" 
        component={DashboardScreen}
        options={{ title: 'Bosh sahifa' }}
      />
      <Tab.Screen 
        name="Balance" 
        component={BalanceScreen}
        options={{ title: 'Balans' }}
      />
      <Tab.Screen 
        name="Statistics" 
        component={StatisticsScreen}
        options={{ title: 'Statistika' }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{ title: 'Profil' }}
      />
    </Tab.Navigator>
  );
}

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = await AsyncStorage.getItem('jwt_token');
      setIsAuthenticated(!!token);
    } catch (error) {
      console.error('Auth check error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return null; // Loading screen can be added here
  }

  return (
    <NavigationContainer>
      <Stack.Navigator>
        {!isAuthenticated ? (
          <Stack.Screen 
            name="Auth" 
            component={TelegramAuthScreen}
            options={{ headerShown: false }}
          />
        ) : (
          <>
            <Stack.Screen 
              name="Main" 
              component={MainTabs}
              options={{ headerShown: false }}
            />
            <Stack.Screen 
              name="Withdraw" 
              component={WithdrawScreen}
              options={{ title: 'Pul yechish' }}
            />
            <Stack.Screen 
              name="SessionHistory" 
              component={SessionHistoryScreen}
              options={{ title: 'Sessiyalar tarixi' }}
            />
            <Stack.Screen 
              name="Support" 
              component={SupportScreen}
              options={{ title: 'Qo\'llab-quvvatlash' }}
            />
            <Stack.Screen 
              name="News" 
              component={NewsScreen}
              options={{ title: 'Yangiliklar' }}
            />
            <Stack.Screen 
              name="Settings" 
              component={SettingsScreen}
              options={{ title: 'Sozlamalar' }}
            />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
