import React, { useEffect, useState } from 'react';
import { View, StyleSheet, Text, FlatList, RefreshControl } from 'react-native';
import Toast from 'react-native-toast-message';

import { SessionApi } from '../api/endpoints';
import { SessionItem, SessionListResponse, SessionSummary } from '../types/api';
import { SectionCard } from '../components/SectionCard';
import { Loader } from '../components/Loader';
import { formatCurrency, formatMb, utcToLocal } from '../utils/format';

const SessionsScreen = () => {
  const [summary, setSummary] = useState<SessionSummary | null>(null);
  const [sessions, setSessions] = useState<SessionItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const load = async () => {
    try {
      setLoading(true);
      const [summaryRes, listRes] = await Promise.all([SessionApi.summary(), SessionApi.list({ limit: 20 })]);
      setSummary(summaryRes.data);
      setSessions(listRes.data.items);
    } catch (error) {
      Toast.show({ type: 'error', text1: 'Sessiyalar olinmadi' });
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    try {
      setRefreshing(true);
      const listRes = await SessionApi.list({ limit: 20 });
      setSessions(listRes.data.items);
    } catch (error) {
      Toast.show({ type: 'error', text1: 'Yangilashda xatolik' });
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <View style={styles.container}>
      <Loader visible={loading} />
      {summary && (
        <SectionCard>
          <Text style={styles.title}>?? Sessiya statistikasi</Text>
          <View style={styles.rowBetween}>
            <Text style={styles.label}>Bugun:</Text>
            <Text style={styles.value}>{summary.today_sessions} sessiya ? {formatMb(summary.today_mb)}</Text>
          </View>
          <View style={styles.rowBetween}>
            <Text style={styles.label}>Hafta:</Text>
            <Text style={styles.value}>{summary.week_sessions} ? {formatMb(summary.week_mb)}</Text>
          </View>
          <View style={styles.rowBetween}>
            <Text style={styles.label}>Daromad (hafta):</Text>
            <Text style={styles.value}>{formatCurrency(summary.week_earnings)}</Text>
          </View>
          <View style={styles.rowBetween}>
            <Text style={styles.label}>O?rtacha sessiya:</Text>
            <Text style={styles.value}>{summary.average_per_session ? formatCurrency(summary.average_per_session) : '?'}</Text>
          </View>
        </SectionCard>
      )}

      <SectionCard>
        <Text style={styles.title}>Sessiyalar tarixi</Text>
        <FlatList
          data={sessions}
          keyExtractor={item => item.id}
          renderItem={({ item }) => <SessionRow item={item} />}
          ItemSeparatorComponent={() => <View style={styles.separator} />}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        />
      </SectionCard>
    </View>
  );
};

const SessionRow: React.FC<{ item: SessionItem }> = ({ item }) => {
  return (
    <View style={styles.sessionRow}>
      <View style={{ flex: 1 }}>
        <Text style={styles.sessionStatus}>{item.status.toUpperCase()}</Text>
        <Text style={styles.sessionDate}>{utcToLocal(item.start_time)}</Text>
        {item.end_time && <Text style={styles.sessionDate}>? {utcToLocal(item.end_time)}</Text>}
      </View>
      <View style={{ alignItems: 'flex-end' }}>
        <Text style={styles.sessionMetric}>{formatMb(item.sent_mb)}</Text>
        <Text style={styles.sessionEarnings}>{formatCurrency(item.earned_usd)}</Text>
      </View>
    </View>
  );
};

export default SessionsScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#050912',
    paddingHorizontal: 20,
    paddingTop: 16,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: '#f8fafc',
    marginBottom: 12,
  },
  rowBetween: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  label: {
    color: '#94a3b8',
  },
  value: {
    color: '#e2e8f0',
    fontWeight: '600',
  },
  separator: {
    height: 1,
    backgroundColor: '#111827',
  },
  sessionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 12,
  },
  sessionStatus: {
    color: '#38bdf8',
    fontWeight: '700',
  },
  sessionDate: {
    color: '#94a3b8',
    fontSize: 12,
  },
  sessionMetric: {
    color: '#f8fafc',
    fontWeight: '600',
  },
  sessionEarnings: {
    color: '#4ade80',
    fontWeight: '700',
  },
});

