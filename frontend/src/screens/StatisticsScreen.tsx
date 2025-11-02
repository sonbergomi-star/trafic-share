import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  Dimensions,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { LineChart, BarChart } from 'react-native-chart-kit';
import { API } from '../api/client';

const screenWidth = Dimensions.get('window').width;

export default function StatisticsScreen() {
  const [loading, setLoading] = useState(true);
  const [dailyStats, setDailyStats] = useState<any>(null);
  const [weeklyStats, setWeeklyStats] = useState<any>(null);
  const [monthlyStats, setMonthlyStats] = useState<any>(null);

  useEffect(() => {
    loadStatistics();
  }, []);

  const loadStatistics = async () => {
    try {
      const userData = await AsyncStorage.getItem('user_data');
      if (userData) {
        const user = JSON.parse(userData);
        
        const [daily, weekly, monthly] = await Promise.all([
          API.getDailyStats(user.telegram_id),
          API.getWeeklyStats(user.telegram_id),
          API.getMonthlyStats(user.telegram_id),
        ]);
        
        setDailyStats(daily.data);
        setWeeklyStats(weekly.data);
        setMonthlyStats(monthly.data);
      }
    } catch (error) {
      console.error('Load statistics error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007bff" />
      </View>
    );
  }

  const chartConfig = {
    backgroundGradientFrom: '#fff',
    backgroundGradientTo: '#fff',
    color: (opacity = 1) => `rgba(0, 123, 255, ${opacity})`,
    strokeWidth: 2,
    barPercentage: 0.5,
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Statistika</Text>

      {/* Daily Stats */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>?? Bugungi statistika</Text>
        {dailyStats && (
          <View style={styles.statsGrid}>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Yuborilgan</Text>
              <Text style={styles.statValue}>
                {dailyStats.sent_mb.toFixed(0)} MB
              </Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Sotilgan</Text>
              <Text style={styles.statValue}>
                {dailyStats.sold_mb.toFixed(0)} MB
              </Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Daromad</Text>
              <Text style={[styles.statValue, styles.profitValue]}>
                ${dailyStats.profit_usd.toFixed(2)}
              </Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Narx/MB</Text>
              <Text style={styles.statValue}>
                ${dailyStats.price_per_mb.toFixed(4)}
              </Text>
            </View>
          </View>
        )}
      </View>

      {/* Weekly Stats */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>?? Haftalik statistika</Text>
        {weeklyStats && (
          <View style={styles.statsGrid}>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Yuborilgan</Text>
              <Text style={styles.statValue}>
                {(weeklyStats.sent_mb / 1024).toFixed(2)} GB
              </Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Sotilgan</Text>
              <Text style={styles.statValue}>
                {(weeklyStats.sold_mb / 1024).toFixed(2)} GB
              </Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Daromad</Text>
              <Text style={[styles.statValue, styles.profitValue]}>
                ${weeklyStats.profit_usd.toFixed(2)}
              </Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>O'rtacha narx</Text>
              <Text style={styles.statValue}>
                ${weeklyStats.avg_price_per_mb.toFixed(4)}
              </Text>
            </View>
          </View>
        )}
      </View>

      {/* Monthly Stats */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>?? Oylik statistika</Text>
        {monthlyStats && (
          <View style={styles.statsGrid}>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Yuborilgan</Text>
              <Text style={styles.statValue}>
                {(monthlyStats.sent_mb / 1024).toFixed(2)} GB
              </Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Sotilgan</Text>
              <Text style={styles.statValue}>
                {(monthlyStats.sold_mb / 1024).toFixed(2)} GB
              </Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Daromad</Text>
              <Text style={[styles.statValue, styles.profitValue]}>
                ${monthlyStats.profit_usd.toFixed(2)}
              </Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>O'rtacha</Text>
              <Text style={styles.statValue}>
                ${monthlyStats.avg_price_per_mb.toFixed(4)}/MB
              </Text>
            </View>
          </View>
        )}
      </View>

      {/* Chart Placeholder */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>?? Trafik dinamikasi</Text>
        <Text style={styles.placeholder}>
          Grafiklar tez orada qo'shiladi...
        </Text>
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
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    margin: 20,
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
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 15,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statItem: {
    width: '48%',
    marginBottom: 15,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 5,
  },
  statValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  profitValue: {
    color: '#28a745',
  },
  placeholder: {
    textAlign: 'center',
    color: '#999',
    fontSize: 14,
    paddingVertical: 20,
  },
});
