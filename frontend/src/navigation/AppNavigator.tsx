import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';

import { useAuth } from '../context/AuthContext';
import AuthScreen from '../screens/AuthScreen';
import DashboardScreen from '../screens/DashboardScreen';
import AnalyticsScreen from '../screens/AnalyticsScreen';
import BalanceScreen from '../screens/BalanceScreen';
import WithdrawScreen from '../screens/WithdrawScreen';
import SessionsScreen from '../screens/SessionsScreen';
import SettingsScreen from '../screens/SettingsScreen';
import SupportScreen from '../screens/SupportScreen';
import NewsScreen from '../screens/NewsScreen';

export type RootStackParamList = {
  Auth: undefined;
  Main: undefined;
};

export type BalanceStackParamList = {
  BalanceHome: undefined;
  Withdraw: undefined;
};

export type SettingsStackParamList = {
  SettingsHome: undefined;
  Support: undefined;
  News: undefined;
};

const RootStack = createNativeStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator();
const BalanceStack = createNativeStackNavigator<BalanceStackParamList>();
const SettingsStack = createNativeStackNavigator<SettingsStackParamList>();

const BalanceStackNavigator = () => (
  <BalanceStack.Navigator>
    <BalanceStack.Screen name="BalanceHome" component={BalanceScreen} options={{ headerShown: false }} />
    <BalanceStack.Screen
      name="Withdraw"
      component={WithdrawScreen}
      options={{ title: 'Pul yechish', headerTintColor: '#fff', headerStyle: { backgroundColor: '#0b0e1a' } }}
    />
  </BalanceStack.Navigator>
);

const SettingsStackNavigator = () => (
  <SettingsStack.Navigator>
    <SettingsStack.Screen name="SettingsHome" component={SettingsScreen} options={{ headerShown: false }} />
    <SettingsStack.Screen
      name="Support"
      component={SupportScreen}
      options={{ title: "Qo?llab-quvvatlash", headerTintColor: '#fff', headerStyle: { backgroundColor: '#0b0e1a' } }}
    />
    <SettingsStack.Screen
      name="News"
      component={NewsScreen}
      options={{ title: 'Yangiliklar & Promo', headerTintColor: '#fff', headerStyle: { backgroundColor: '#0b0e1a' } }}
    />
  </SettingsStack.Navigator>
);

const MainTabs = () => {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarStyle: { backgroundColor: '#050912', borderTopColor: '#111827' },
        tabBarActiveTintColor: '#4ade80',
        tabBarInactiveTintColor: '#94a3b8',
        tabBarIcon: ({ color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap = 'grid-outline';
          switch (route.name) {
            case 'Dashboard':
              iconName = 'speedometer-outline';
              break;
            case 'Analytics':
              iconName = 'analytics-outline';
              break;
            case 'Balance':
              iconName = 'wallet-outline';
              break;
            case 'Sessions':
              iconName = 'time-outline';
              break;
            case 'Settings':
              iconName = 'settings-outline';
              break;
          }
          return <Ionicons name={iconName} size={size} color={color} />;
        },
      })}
    >
      <Tab.Screen name="Dashboard" component={DashboardScreen} options={{ title: 'Dashboard' }} />
      <Tab.Screen name="Analytics" component={AnalyticsScreen} options={{ title: 'Statistika' }} />
      <Tab.Screen name="Balance" component={BalanceStackNavigator} options={{ title: 'Balans' }} />
      <Tab.Screen name="Sessions" component={SessionsScreen} options={{ title: 'Sessiyalar' }} />
      <Tab.Screen name="Settings" component={SettingsStackNavigator} options={{ title: 'Sozlamalar' }} />
    </Tab.Navigator>
  );
};

const AppNavigator = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return null;
  }

  return (
    <NavigationContainer>
      <RootStack.Navigator screenOptions={{ headerShown: false }}>
        {user ? (
          <RootStack.Screen name="Main" component={MainTabs} />
        ) : (
          <RootStack.Screen name="Auth" component={AuthScreen} />
        )}
      </RootStack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator;

