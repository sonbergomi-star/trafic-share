import React, { useEffect, useState } from 'react';
import { View, StyleSheet, Text, Dimensions, TouchableOpacity, ScrollView } from 'react-native';
import { LineChart, BarChart } from 'react-native-chart-kit';
import Toast from 'react-native-toast-message';

import { AnalyticsApi } from '../api/endpoints';
import { useAuth } from '../context/AuthContext';
import { AnalyticsPoint, AnalyticsResponse } from '../types/api';
import { SectionCard } from '../components/SectionCard';
import { Loader } from '../components/Loader';

const chartConfig = {
  backgroundGradientFrom: '#101727',
  backgroundGradientTo: '#101727',
  color: (opacity = 1) => `rgba(74, 222, 128, ${opacity})`,
  labelColor: (opacity = 1) => `rgba(226, 232, 240, ${opacity})`,
  decimalPlaces: 2,
};

const PERIODS: Array<{ key: 'daily' | 'weekly' | 'monthly'; label: string }> = [
  { key: 'daily', label: 'Kunlik' },
  { key: 'weekly', label: 'Haftalik' },
  { key: 'monthly', label: 'Oylik' },
];

const AnalyticsScreen = () => {
  const { user } = useAuth();
  const [period, setPeriod] = useState<'daily' | 'weekly' | 'monthly'>('daily');
  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchData = async (selected: typeof period) => {
    if (!user) return;
    try {
      setLoading(true);
      let response;
      switch (selected) {
        case 'daily':
          response = await AnalyticsApi.daily(user.telegram_id);
          break;
        case 'weekly':
          response = await AnalyticsApi.weekly(user.telegram_id);
          break;
        case 'monthly':
          response = await AnalyticsApi.monthly(user.telegram_id);
          break;
      }
      setAnalytics(response.data);
    } catch (error) {
      Toast.show({ type: 'error', text1: 'Statistika olinmadi' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData(period);
  }, [user?.telegram_id, period]);

  const renderChart = (points: AnalyticsPoint[]) => {
    if (!points.length) {
      return <Text style={styles.empty}>Hali statistik ma?lumot yo?q</Text>;
    }

    const labels = points.map(point => point.date.slice(-5));
    const dataMb = points.map(point => point.sent_mb);
    const dataUsd = points.map(point => point.profit_usd);

    return (
      <View>
        <Text style={styles.chartLabel}>Trafik yuborilgan (MB)</Text>
        <BarChart
          width={Dimensions.get('window').width - 60}
          height={220}
          data={{ labels, datasets: [{ data: dataMb }] }}
          chartConfig={chartConfig}
          style={styles.chart}
        />
        <Text style={styles.chartLabel}>Daromad (USD)</Text>
        <LineChart
          width={Dimensions.get('window').width - 60}
          height={220}
          data={{ labels, datasets: [{ data: dataUsd }] }}
          chartConfig={chartConfig}
          bezier
          style={styles.chart}
        />
      </View>
    );
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 40 }}>
      <Text style={styles.title}>?? Statistika</Text>
      <Text style={styles.subtitle}>Kunlik, haftalik va oylik tahlillarni kuzating.</Text>
      <View style={styles.periodRow}>
        {PERIODS.map(item => (
          <TouchableOpacity
            key={item.key}
            style={[styles.periodBtn, period === item.key && styles.periodBtnActive]}
            onPress={() => setPeriod(item.key)}
          >
            <Text style={[styles.periodLabel, period === item.key && styles.periodLabelActive]}>{item.label}</Text>
          </TouchableOpacity>
        ))}
      </View>
      <Loader visible={loading} />
      {analytics && <SectionCard>{renderChart(analytics.points)}</SectionCard>}
    </ScrollView>
  );
};

export default AnalyticsScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#050912',
    paddingHorizontal: 20,
    paddingTop: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: '#e2e8f0',
  },
  subtitle: {
    color: '#94a3b8',
    marginBottom: 16,
  },
  periodRow: {
    flexDirection: 'row',
    marginBottom: 16,
    backgroundColor: '#101727',
    borderRadius: 14,
    padding: 6,
  },
  periodBtn: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 12,
    alignItems: 'center',
  },
  periodBtnActive: {
    backgroundColor: '#1d4ed8',
  },
  periodLabel: {
    color: '#94a3b8',
    fontWeight: '600',
  },
  periodLabelActive: {
    color: '#f8fafc',
  },
  chart: {
    marginVertical: 12,
    borderRadius: 16,
  },
  chartLabel: {
    color: '#cbd5f5',
    fontWeight: '600',
    marginTop: 8,
  },
  empty: {
    color: '#94a3b8',
    textAlign: 'center',
    paddingVertical: 20,
  },
});

