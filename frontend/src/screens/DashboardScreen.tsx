import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
  Image,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API } from '../api/client';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

export default function DashboardScreen({ navigation }: any) {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [sessionActive, setSessionActive] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const userData = await AsyncStorage.getItem('user_data');
      if (userData) {
        const user = JSON.parse(userData);
        const response = await API.getDashboard(user.telegram_id);
        setDashboardData(response.data);
      }
    } catch (error) {
      console.error('Load dashboard error:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleStartStop = async () => {
    try {
      const userData = await AsyncStorage.getItem('user_data');
      if (!userData) return;

      const user = JSON.parse(userData);

      if (!sessionActive) {
        // Start session
        const response = await API.startSession({
          telegram_id: user.telegram_id,
          device_id: 'android_device',
          network_type: 'wifi',
        });
        
        if (response.data.status === 'ok') {
          setSessionActive(true);
          setCurrentSessionId(response.data.session_id);
        }
      } else {
        // Stop session
        if (currentSessionId) {
          await API.stopSession(currentSessionId);
          setSessionActive(false);
          setCurrentSessionId(null);
        }
      }
    } catch (error) {
      console.error('Start/Stop error:', error);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadDashboard();
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007bff" />
      </View>
    );
  }

  if (!dashboardData) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Ma'lumot yuklanmadi</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Profile Block */}
      <View style={styles.profileBlock}>
        <View style={styles.profileInfo}>
          {dashboardData.user.photo_url ? (
            <Image
              source={{ uri: dashboardData.user.photo_url }}
              style={styles.avatar}
            />
          ) : (
            <View style={styles.avatarPlaceholder}>
              <Icon name="account" size={40} color="#fff" />
            </View>
          )}
          <View style={styles.profileText}>
            <Text style={styles.profileName}>
              {dashboardData.user.first_name}
            </Text>
            <Text style={styles.profileUsername}>
              @{dashboardData.user.username}
            </Text>
          </View>
        </View>
      </View>

      {/* Balance Block */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>?? Balans</Text>
        <Text style={styles.balanceAmount}>
          ${dashboardData.balance.usd.toFixed(2)}
        </Text>
      </View>

      {/* Price Block */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>?? Bugungi narx</Text>
        <Text style={styles.priceAmount}>
          ${dashboardData.pricing.price_per_gb.toFixed(2)} / GB
        </Text>
        {dashboardData.pricing.message && (
          <Text style={styles.priceMessage}>
            {dashboardData.pricing.message}
          </Text>
        )}
      </View>

      {/* Traffic Block */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>?? Trafik</Text>
        <View style={styles.trafficRow}>
          <Text style={styles.trafficLabel}>Yuborilgan:</Text>
          <Text style={styles.trafficValue}>
            {dashboardData.traffic.sent_mb.toFixed(2)} MB
          </Text>
        </View>
        <View style={styles.trafficRow}>
          <Text style={styles.trafficLabel}>Ishlatilgan:</Text>
          <Text style={styles.trafficValue}>
            {dashboardData.traffic.used_mb.toFixed(2)} MB
          </Text>
        </View>
        <View style={styles.trafficRow}>
          <Text style={styles.trafficLabel}>Qolgan:</Text>
          <Text style={styles.trafficValue}>
            {dashboardData.traffic.remaining_mb.toFixed(2)} MB
          </Text>
        </View>
      </View>

      {/* Action Buttons */}
      <View style={styles.actionsContainer}>
        <TouchableOpacity
          style={[
            styles.actionButton,
            sessionActive ? styles.stopButton : styles.startButton,
          ]}
          onPress={handleStartStop}
        >
          <Text style={styles.actionButtonText}>
            {sessionActive ? '?? STOP' : '?? START'}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.actionButton, styles.withdrawButton]}
          onPress={() => navigation.navigate('Withdraw')}
          disabled={dashboardData.balance.usd < 1.39}
        >
          <Text style={styles.actionButtonText}>?? YECHISH</Text>
        </TouchableOpacity>
      </View>

      {/* Quick Actions */}
      <View style={styles.quickActions}>
        <TouchableOpacity
          style={styles.quickActionButton}
          onPress={() => navigation.navigate('SessionHistory')}
        >
          <Icon name="history" size={24} color="#007bff" />
          <Text style={styles.quickActionText}>Sessiyalar</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.quickActionButton}
          onPress={() => navigation.navigate('Support')}
        >
          <Icon name="help-circle" size={24} color="#007bff" />
          <Text style={styles.quickActionText}>Yordam</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.quickActionButton}
          onPress={() => navigation.navigate('News')}
        >
          <Icon name="newspaper" size={24} color="#007bff" />
          <Text style={styles.quickActionText}>Yangiliklar</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.quickActionButton}
          onPress={() => navigation.navigate('Settings')}
        >
          <Icon name="cog" size={24} color="#007bff" />
          <Text style={styles.quickActionText}>Sozlamalar</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  profileBlock: {
    backgroundColor: '#007bff',
    padding: 20,
    paddingTop: 40,
  },
  profileInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {
    width: 60,
    height: 60,
    borderRadius: 30,
  },
  avatarPlaceholder: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#0056b3',
    justifyContent: 'center',
    alignItems: 'center',
  },
  profileText: {
    marginLeft: 15,
  },
  profileName: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
  },
  profileUsername: {
    color: '#e0e0e0',
    fontSize: 14,
  },
  card: {
    backgroundColor: '#fff',
    margin: 15,
    padding: 20,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 10,
  },
  balanceAmount: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#28a745',
  },
  priceAmount: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#007bff',
  },
  priceMessage: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
  },
  trafficRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginVertical: 5,
  },
  trafficLabel: {
    fontSize: 14,
    color: '#666',
  },
  trafficValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  actionsContainer: {
    flexDirection: 'row',
    paddingHorizontal: 15,
    marginBottom: 15,
  },
  actionButton: {
    flex: 1,
    paddingVertical: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginHorizontal: 5,
  },
  startButton: {
    backgroundColor: '#28a745',
  },
  stopButton: {
    backgroundColor: '#dc3545',
  },
  withdrawButton: {
    backgroundColor: '#ffc107',
  },
  actionButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  quickActions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 15,
    marginBottom: 20,
  },
  quickActionButton: {
    width: '45%',
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    margin: '2.5%',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  quickActionText: {
    marginTop: 8,
    fontSize: 12,
    color: '#333',
  },
});
