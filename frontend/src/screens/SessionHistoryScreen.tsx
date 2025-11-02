import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  RefreshControl,
  TouchableOpacity,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { API } from '../api/client';

export default function SessionHistoryScreen() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [sessions, setSessions] = useState<any[]>([]);
  const [summary, setSummary] = useState({
    today: { sessions: 0, mb: 0, earnings: 0 },
    week: { sessions: 0, mb: 0, earnings: 0 },
  });

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const userData = await AsyncStorage.getItem('user_data');
      if (userData) {
        const user = JSON.parse(userData);
        const response = await API.getSessions(user.telegram_id);
        setSessions(response.data.sessions);
        calculateSummary(response.data.sessions);
      }
    } catch (error) {
      console.error('Load sessions error:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const calculateSummary = (sessionsList: any[]) => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);

    let todaySessions = 0;
    let todayMb = 0;
    let todayEarnings = 0;
    let weekSessions = 0;
    let weekMb = 0;
    let weekEarnings = 0;

    sessionsList.forEach((session) => {
      const sessionDate = new Date(session.start_time);
      
      if (sessionDate >= today) {
        todaySessions++;
        todayMb += session.sent_mb || 0;
        todayEarnings += session.earned_usd || 0;
      }
      
      if (sessionDate >= weekAgo) {
        weekSessions++;
        weekMb += session.sent_mb || 0;
        weekEarnings += session.earned_usd || 0;
      }
    });

    setSummary({
      today: { sessions: todaySessions, mb: todayMb, earnings: todayEarnings },
      week: { sessions: weekSessions, mb: weekMb, earnings: weekEarnings },
    });
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadSessions();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return '#28a745';
      case 'completed':
        return '#007bff';
      case 'failed':
        return '#dc3545';
      case 'cancelled':
        return '#6c757d';
      default:
        return '#999';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return 'play-circle';
      case 'completed':
        return 'check-circle';
      case 'failed':
        return 'alert-circle';
      case 'cancelled':
        return 'close-circle';
      default:
        return 'help-circle';
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007bff" />
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
      {/* Summary Cards */}
      <View style={styles.summaryContainer}>
        <View style={styles.summaryCard}>
          <Text style={styles.summaryTitle}>Bugun</Text>
          <Text style={styles.summaryValue}>{summary.today.sessions} sessiya</Text>
          <Text style={styles.summarySubtext}>
            {summary.today.mb.toFixed(0)} MB ? ${summary.today.earnings.toFixed(2)}
          </Text>
        </View>

        <View style={styles.summaryCard}>
          <Text style={styles.summaryTitle}>Hafta</Text>
          <Text style={styles.summaryValue}>{summary.week.sessions} sessiya</Text>
          <Text style={styles.summarySubtext}>
            {(summary.week.mb / 1024).toFixed(2)} GB ? ${summary.week.earnings.toFixed(2)}
          </Text>
        </View>
      </View>

      {/* Sessions List */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Sessiyalar tarixi</Text>

        {sessions.length === 0 ? (
          <View style={styles.emptyState}>
            <Icon name="history" size={64} color="#ddd" />
            <Text style={styles.emptyText}>Hali sessiyalar yo'q</Text>
            <Text style={styles.emptySubtext}>
              Trafik ulashishni boshlang
            </Text>
          </View>
        ) : (
          sessions.map((session) => (
            <View key={session.id} style={styles.sessionCard}>
              <View style={styles.sessionHeader}>
                <View style={styles.sessionHeaderLeft}>
                  <Icon
                    name={getStatusIcon(session.status)}
                    size={20}
                    color={getStatusColor(session.status)}
                  />
                  <Text style={styles.sessionDate}>
                    {new Date(session.start_time).toLocaleDateString('uz-UZ')}
                  </Text>
                </View>
                <Text
                  style={[
                    styles.sessionStatus,
                    { color: getStatusColor(session.status) },
                  ]}
                >
                  {session.status}
                </Text>
              </View>

              <View style={styles.sessionDetails}>
                <View style={styles.sessionDetailRow}>
                  <Icon name="clock-outline" size={16} color="#666" />
                  <Text style={styles.sessionDetailText}>
                    {session.duration || 'N/A'}
                  </Text>
                </View>

                <View style={styles.sessionDetailRow}>
                  <Icon name="upload" size={16} color="#666" />
                  <Text style={styles.sessionDetailText}>
                    {session.sent_mb?.toFixed(0) || '0'} MB
                  </Text>
                </View>

                <View style={styles.sessionDetailRow}>
                  <Icon name="cash" size={16} color="#28a745" />
                  <Text style={[styles.sessionDetailText, styles.earningsText]}>
                    ${session.earned_usd?.toFixed(3) || '0.000'}
                  </Text>
                </View>
              </View>

              {session.device && (
                <View style={styles.sessionFooter}>
                  <Text style={styles.sessionDevice}>
                    {session.device} ? {session.network_type}
                  </Text>
                  {session.location && (
                    <Text style={styles.sessionLocation}>
                      ?? {session.location}
                    </Text>
                  )}
                </View>
              )}
            </View>
          ))
        )}
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
  summaryContainer: {
    flexDirection: 'row',
    padding: 15,
    gap: 15,
  },
  summaryCard: {
    flex: 1,
    backgroundColor: '#007bff',
    padding: 15,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  summaryTitle: {
    color: '#e0e0e0',
    fontSize: 12,
    marginBottom: 5,
  },
  summaryValue: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  summarySubtext: {
    color: '#e0e0e0',
    fontSize: 11,
  },
  section: {
    padding: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  emptyState: {
    backgroundColor: '#fff',
    padding: 40,
    borderRadius: 10,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    color: '#999',
    marginTop: 15,
  },
  emptySubtext: {
    fontSize: 12,
    color: '#ccc',
    marginTop: 5,
  },
  sessionCard: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  sessionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  sessionHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  sessionDate: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  sessionStatus: {
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  sessionDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  sessionDetailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
  },
  sessionDetailText: {
    fontSize: 12,
    color: '#666',
  },
  earningsText: {
    color: '#28a745',
    fontWeight: '600',
  },
  sessionFooter: {
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
    paddingTop: 8,
  },
  sessionDevice: {
    fontSize: 11,
    color: '#999',
  },
  sessionLocation: {
    fontSize: 11,
    color: '#999',
    marginTop: 3,
  },
});
