import React, { useState } from 'react';
import { View, StyleSheet, Text, Switch, TouchableOpacity } from 'react-native';
import Toast from 'react-native-toast-message';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useNavigation } from '@react-navigation/native';

import { useAuth } from '../context/AuthContext';
import { UserApi } from '../api/endpoints';
import { SettingsStackParamList } from '../navigation/AppNavigator';

type NavigationProp = NativeStackNavigationProp<SettingsStackParamList, 'SettingsHome'>;

const SettingsScreen = () => {
  const { user, logout } = useAuth();
  const navigation = useNavigation<NavigationProp>();
  const [pushEnabled, setPushEnabled] = useState(user?.notifications_enabled ?? true);
  const [systemEnabled, setSystemEnabled] = useState(true);

  const persist = async (payload: Record<string, unknown>) => {
    try {
      await UserApi.updateSettings(payload);
      Toast.show({ type: 'success', text1: 'Sozlamalar yangilandi' });
    } catch (error) {
      Toast.show({ type: 'error', text1: 'Saqlashda xatolik' });
    }
  };

  const handleLogout = async () => {
    try {
      await UserApi.logout();
    } catch (error) {
      // ignore
    } finally {
      await logout();
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.header}>?? Sozlamalar</Text>
      <Text style={styles.caption}>Bildirishnomalar va xavfsizlikni boshqaring.</Text>

      <View style={styles.block}>
        <View style={styles.rowBetween}>
          <Text style={styles.label}>Push bildirishnomalar</Text>
          <Switch
            value={pushEnabled}
            onValueChange={value => {
              setPushEnabled(value);
              persist({ push_notifications: value });
            }}
          />
        </View>
        <View style={styles.rowBetween}>
          <Text style={styles.label}>Tizim yangiliklari</Text>
          <Switch
            value={systemEnabled}
            onValueChange={value => {
              setSystemEnabled(value);
              persist({ system_updates: value });
            }}
          />
        </View>
      </View>

      <View style={styles.block}>
        <TouchableOpacity style={styles.navRow} onPress={() => navigation.navigate('Support')}>
          <Text style={styles.navText}>?? Qo?llab-quvvatlash</Text>
          <Text style={styles.navMeta}>Chat, ticketlar</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.navRow} onPress={() => navigation.navigate('News')}>
          <Text style={styles.navText}>?? Yangiliklar & Promo</Text>
          <Text style={styles.navMeta}>Aksiyalar, promo kodlar</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity style={styles.logoutBtn} onPress={handleLogout}>
        <Text style={styles.logoutLabel}>?? Hisobdan chiqish</Text>
      </TouchableOpacity>
    </View>
  );
};

export default SettingsScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#050912',
    paddingHorizontal: 20,
    paddingTop: 24,
  },
  header: {
    fontSize: 24,
    fontWeight: '700',
    color: '#f8fafc',
  },
  caption: {
    color: '#94a3b8',
    marginBottom: 24,
  },
  block: {
    backgroundColor: '#101727',
    borderRadius: 16,
    padding: 16,
    marginBottom: 20,
  },
  rowBetween: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  label: {
    color: '#e2e8f0',
    fontSize: 16,
  },
  navRow: {
    marginBottom: 16,
  },
  navText: {
    color: '#f8fafc',
    fontSize: 16,
    fontWeight: '600',
  },
  navMeta: {
    color: '#64748b',
    marginTop: 4,
  },
  logoutBtn: {
    paddingVertical: 14,
    alignItems: 'center',
    borderRadius: 16,
    backgroundColor: '#ef4444',
  },
  logoutLabel: {
    color: '#fff1f2',
    fontWeight: '700',
    fontSize: 16,
  },
});

