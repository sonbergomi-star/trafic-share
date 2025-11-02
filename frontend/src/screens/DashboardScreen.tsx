import React, { useEffect, useState } from 'react';
import { View, StyleSheet, Text, TouchableOpacity, ScrollView } from 'react-native';
import Toast from 'react-native-toast-message';

import { DashboardApi, TrafficApi } from '../api/endpoints';
import { useAuth } from '../context/AuthContext';
import { DashboardResponse } from '../types/api';
import { SectionCard } from '../components/SectionCard';
import { Loader } from '../components/Loader';
import { formatCurrency, formatMb, formatSpeed } from '../utils/format';

const DashboardScreen = () => {
  const { user } = useAuth();
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchDashboard = async () => {
    if (!user) return;
    try {
      setLoading(true);
      const response = await DashboardApi.getDashboard(user.telegram_id);
      setData(response.data);
    } catch (error) {
      Toast.show({ type: 'error', text1: "Ma'lumotlar yuklanmadi" });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, [user?.telegram_id]);

  const startTraffic = async () => {
    try {
      await TrafficApi.start({ device_id: 'android-device', network_type: 'mobile', app_version: '1.0.0' });
      Toast.show({ type: 'success', text1: 'Sessiya boshlandi' });
      fetchDashboard();
    } catch (error) {
      Toast.show({ type: 'error', text1: 'START ishlamadi' });
    }
  };

  const stopTraffic = async () => {
    if (!data?.traffic.session_id) {
      Toast.show({ type: 'info', text1: 'Aktiv sessiya topilmadi' });
      return;
    }
    try {
      await TrafficApi.stop(data.traffic.session_id);
      Toast.show({ type: 'success', text1: 'Sessiya to?xtatildi' });
      fetchDashboard();
    } catch (error) {
      Toast.show({ type: 'error', text1: 'STOP ishlamadi' });
    }
  };

  if (!user) {
    return null;
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 48 }}>
      <Text style={styles.greeting}>?? Salom, {user.first_name || user.username}</Text>
      <Text style={styles.caption}>Keling, bugungi faoliyatni ko?rib chiqamiz.</Text>
      <Loader visible={loading} />

      {data && (
        <>
          <SectionCard>
            <Text style={styles.cardTitle}>Balans</Text>
            <Text style={styles.balance}>{formatCurrency(data.balance.usd)}</Text>
            <Text style={styles.balanceSub}>USDT: {formatCurrency(data.balance.converted_usdt, 'USDT')}</Text>
            <Text style={styles.balanceSub}>UZS: {formatCurrency(data.balance.converted_uzs, 'UZS')}</Text>
            <TouchableOpacity style={styles.actionPrimary} onPress={() => Toast.show({ text1: 'Yaqinda', type: 'info' })}>
              <Text style={styles.actionPrimaryLabel}>?? Pul yechish</Text>
            </TouchableOpacity>
          </SectionCard>

          <SectionCard>
            <Text style={styles.cardTitle}>Trafik holati</Text>
            <View style={styles.rowBetween}>
              <Text style={styles.metricLabel}>Yuborilgan</Text>
              <Text style={styles.metricValue}>{formatMb(data.traffic.sent_mb)}</Text>
            </View>
            <View style={styles.rowBetween}>
              <Text style={styles.metricLabel}>Ishlatilgan</Text>
              <Text style={[styles.metricValue, { color: '#f87171' }]}>{formatMb(data.traffic.used_mb)}</Text>
            </View>
            <View style={styles.rowBetween}>
              <Text style={styles.metricLabel}>Qolgan</Text>
              <Text style={[styles.metricValue, { color: '#4ade80' }]}>{formatMb(data.traffic.remaining_mb)}</Text>
            </View>
            <View style={styles.rowBetween}>
              <Text style={styles.metricLabel}>Tezlik</Text>
              <Text style={styles.metricValue}>{formatSpeed(data.traffic.current_speed)}</Text>
            </View>
            <View style={styles.statusBadge}>
              <Text style={styles.statusText}>Status: {data.traffic.status || 'inactive'}</Text>
            </View>
            <View style={styles.actionsRow}>
              <TouchableOpacity style={[styles.actionBtn, { backgroundColor: '#22c55e' }]} onPress={startTraffic}>
                <Text style={styles.actionLabel}>START</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.actionBtn, { backgroundColor: '#ef4444' }]} onPress={stopTraffic}>
                <Text style={styles.actionLabel}>STOP</Text>
              </TouchableOpacity>
            </View>
          </SectionCard>

          <SectionCard>
            <Text style={styles.cardTitle}>Bugungi narx</Text>
            <Text style={styles.price}>${data.pricing.price_per_gb.toFixed(2)} / GB</Text>
            {data.pricing.change !== undefined && (
              <Text style={{ color: data.pricing.change >= 0 ? '#4ade80' : '#f87171' }}>
                {data.pricing.change >= 0 ? '?' : '?'} {Math.abs(data.pricing.change).toFixed(2)} o?zgarish
              </Text>
            )}
            {data.pricing.message && <Text style={styles.priceMessage}>{data.pricing.message}</Text>}
          </SectionCard>

          <SectionCard>
            <Text style={styles.cardTitle}>Mini statistika</Text>
            <View style={styles.rowBetween}>
              <Text style={styles.metricLabel}>Bugun</Text>
              <Text style={styles.metricValue}>{formatCurrency(data.mini_stats.today_earn)}</Text>
            </View>
            <View style={styles.rowBetween}>
              <Text style={styles.metricLabel}>7 kun</Text>
              <Text style={styles.metricValue}>{formatCurrency(data.mini_stats.week_earn)}</Text>
            </View>
            <View style={styles.rowBetween}>
              <Text style={styles.metricLabel}>Oy</Text>
              <Text style={styles.metricValue}>{formatCurrency(data.mini_stats.month_earn)}</Text>
            </View>
          </SectionCard>
        </>
      )}
    </ScrollView>
  );
};

export default DashboardScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#050912',
    paddingHorizontal: 20,
    paddingTop: 16,
  },
  greeting: {
    fontSize: 24,
    color: '#e2e8f0',
    fontWeight: '700',
  },
  caption: {
    color: '#94a3b8',
    marginBottom: 16,
  },
  cardTitle: {
    color: '#f8fafc',
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 12,
  },
  balance: {
    fontSize: 32,
    fontWeight: '700',
    color: '#38bdf8',
    marginBottom: 4,
  },
  balanceSub: {
    color: '#94a3b8',
  },
  rowBetween: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  metricLabel: {
    color: '#94a3b8',
  },
  metricValue: {
    color: '#f8fafc',
    fontWeight: '600',
  },
  statusBadge: {
    marginTop: 12,
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 999,
    alignSelf: 'flex-start',
    backgroundColor: '#1e293b',
  },
  statusText: {
    color: '#f8fafc',
    fontSize: 13,
  },
  actionsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 16,
  },
  actionBtn: {
    flex: 1,
    paddingVertical: 12,
    marginHorizontal: 4,
    borderRadius: 12,
    alignItems: 'center',
  },
  actionLabel: {
    color: '#0f172a',
    fontWeight: '700',
  },
  price: {
    fontSize: 28,
    color: '#fbbf24',
    fontWeight: '700',
    marginBottom: 8,
  },
  priceMessage: {
    color: '#94a3b8',
  },
  actionPrimary: {
    marginTop: 20,
    backgroundColor: '#4ade80',
    paddingVertical: 14,
    borderRadius: 16,
    alignItems: 'center',
  },
  actionPrimaryLabel: {
    color: '#052e16',
    fontWeight: '700',
    fontSize: 16,
  },
});

