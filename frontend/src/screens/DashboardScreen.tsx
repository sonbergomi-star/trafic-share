import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  ScrollView,
  RefreshControl,
  StyleSheet,
  Alert,
} from 'react-native';
import { AnimatedBalance } from '../components/AnimatedBalance';
import { TrafficProgressBar } from '../components/TrafficProgressBar';
import { SessionCard } from '../components/SessionCard';
import { useAuth } from '../hooks/useAuth';
import { useWebSocket } from '../hooks/useWebSocket';
import { api } from '../services/api';
import ForegroundService from '../services/ForegroundService';

/**
 * REAL Dashboard screen with animations and live updates
 */
export const DashboardScreen: React.FC = () => {
  const { user } = useAuth();
  
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [balance, setBalance] = useState(0);
  const [previousBalance, setPreviousBalance] = useState(0);
  const [sentMB, setSentMB] = useState(0);
  const [usedMB, setUsedMB] = useState(0);
  
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionDuration, setSessionDuration] = useState('00:00:00');
  const [sessionMB, setSessionMB] = useState(0);
  const [sessionSpeed, setSessionSpeed] = useState(0);
  const [sessionEarnings, setSessionEarnings] = useState(0);

  // WebSocket for real-time updates
  const { isConnected, lastMessage } = useWebSocket();

  // Load dashboard data
  const loadDashboard = useCallback(async () => {
    try {
      const response = await api.get(`/dashboard/${user?.telegram_id}`);
      const data = response.data.data;
      
      setPreviousBalance(balance);
      setBalance(data.balance.usd);
      setSentMB(data.traffic.sent_mb);
      setUsedMB(data.traffic.used_mb);
    } catch (error) {
      console.error('? Failed to load dashboard:', error);
    }
  }, [user, balance]);

  // Pull to refresh
  const onRefresh = useCallback(async () => {
    setIsRefreshing(true);
    await loadDashboard();
    setIsRefreshing(false);
  }, [loadDashboard]);

  // Handle WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      const message = JSON.parse(lastMessage.data);
      
      if (message.type === 'session_update') {
        setSessionMB(message.mb_sent);
        setSessionSpeed(message.speed_mbps);
        setSessionEarnings(message.estimated_earnings);
        
        // Update foreground service notification
        if (isSessionActive) {
          ForegroundService.updateNotification({
            sessionId: message.session_id,
            mbSent: message.mb_sent,
            speedMbps: message.speed_mbps,
            durationSec: message.duration_sec,
            estimatedEarnings: message.estimated_earnings,
          });
        }
      } else if (message.type === 'balance_update') {
        setPreviousBalance(balance);
        setBalance(message.new_balance);
      }
    }
  }, [lastMessage, isSessionActive, balance]);

  // Start session
  const handleStartSession = async () => {
    try {
      const response = await api.post('/traffic/start', {
        telegram_id: user?.telegram_id,
      });
      
      if (response.data.status === 'ok') {
        setIsSessionActive(true);
        setSessionId(response.data.session_id);
        
        // Start foreground service
        await ForegroundService.start(response.data.session_id);
        
        Alert.alert('? Sessiya boshlandi', 'Trafik ulashish boshlandi!');
      } else {
        Alert.alert('? Xato', response.data.message || 'Sessiya boshlanmadi');
      }
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Xatolik yuz berdi';
      Alert.alert('? Xato', errorMsg);
    }
  };

  // Stop session
  const handleStopSession = async () => {
    if (!sessionId) return;
    
    Alert.alert(
      '?? Tasdiqlash',
      'Sessiyani to\'xtatishni xohlaysizmi?',
      [
        { text: 'Yo\'q', style: 'cancel' },
        {
          text: 'Ha',
          onPress: async () => {
            try {
              await api.post('/traffic/stop', {
                telegram_id: user?.telegram_id,
                session_id: sessionId,
              });
              
              // Stop foreground service
              await ForegroundService.stop();
              
              setIsSessionActive(false);
              setSessionId(null);
              setSessionMB(0);
              setSessionSpeed(0);
              setSessionEarnings(0);
              
              // Reload dashboard
              await loadDashboard();
              
              Alert.alert('? Sessiya to\'xtatildi', 'Daromad balansingizga qo\'shildi!');
            } catch (error) {
              console.error('? Failed to stop session:', error);
              Alert.alert('? Xato', 'Sessiyani to\'xtatishda xatolik');
            }
          },
        },
      ]
    );
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.content}>
        {/* Animated Balance */}
        <AnimatedBalance
          balance={balance}
          previousBalance={previousBalance}
        />

        {/* Session Control */}
        <SessionCard
          isActive={isSessionActive}
          sessionId={sessionId || undefined}
          duration={sessionDuration}
          mbSent={sessionMB}
          speedMbps={sessionSpeed}
          estimatedEarnings={sessionEarnings}
          onStart={handleStartSession}
          onStop={handleStopSession}
        />

        {/* Traffic Progress */}
        <TrafficProgressBar
          sentMB={sentMB}
          usedMB={usedMB}
        />
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#121212',
  },
  content: {
    padding: 16,
  },
});
