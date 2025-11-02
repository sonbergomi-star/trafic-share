import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API } from '../api/client';

export default function BalanceScreen({ navigation }: any) {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [balanceData, setBalanceData] = useState<any>(null);

  useEffect(() => {
    loadBalance();
  }, []);

  const loadBalance = async () => {
    try {
      const userData = await AsyncStorage.getItem('user_data');
      if (userData) {
        const user = JSON.parse(userData);
        const response = await API.getBalance(user.telegram_id);
        setBalanceData(response.data);
      }
    } catch (error) {
      console.error('Load balance error:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefreshBalance = async () => {
    try {
      const userData = await AsyncStorage.getItem('user_data');
      if (userData) {
        const user = JSON.parse(userData);
        await API.refreshBalance(user.telegram_id);
        loadBalance();
      }
    } catch (error) {
      console.error('Refresh balance error:', error);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadBalance();
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007bff" />
      </View>
    );
  }

  if (!balanceData) {
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
      {/* Balance Card */}
      <View style={styles.balanceCard}>
        <Text style={styles.balanceLabel}>Joriy balans</Text>
        <Text style={styles.balanceAmount}>
          ${balanceData.balance.usd.toFixed(2)}
        </Text>

        <View style={styles.trafficInfo}>
          <View style={styles.trafficItem}>
            <Text style={styles.trafficLabel}>Yuborilgan:</Text>
            <Text style={styles.trafficValue}>
              {balanceData.traffic.sent_mb.toFixed(2)} MB
            </Text>
          </View>
          <View style={styles.trafficItem}>
            <Text style={styles.trafficLabel}>Ishlatilgan:</Text>
            <Text style={styles.trafficValue}>
              {balanceData.traffic.used_mb.toFixed(2)} MB
            </Text>
          </View>
        </View>

        <View style={styles.buttonRow}>
          <TouchableOpacity
            style={styles.refreshButton}
            onPress={handleRefreshBalance}
          >
            <Text style={styles.refreshButtonText}>?? Yangilash</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.withdrawButton,
              balanceData.balance.usd < 1.39 && styles.withdrawButtonDisabled,
            ]}
            onPress={() => navigation.navigate('Withdraw')}
            disabled={balanceData.balance.usd < 1.39}
          >
            <Text style={styles.withdrawButtonText}>?? Yechish</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Transactions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Tranzaksiya tarixi</Text>
        
        {balanceData.transactions.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyText}>Hali tranzaksiyalar yo'q</Text>
          </View>
        ) : (
          balanceData.transactions.map((transaction: any) => (
            <View key={transaction.id} style={styles.transactionCard}>
              <View style={styles.transactionHeader}>
                <Text style={styles.transactionType}>
                  {transaction.type === 'income' ? '?? Daromad' : '?? Yechish'}
                </Text>
                <Text
                  style={[
                    styles.transactionAmount,
                    transaction.type === 'income'
                      ? styles.incomeAmount
                      : styles.withdrawAmount,
                  ]}
                >
                  {transaction.type === 'income' ? '+' : '-'}$
                  {Math.abs(transaction.amount_usd).toFixed(2)}
                </Text>
              </View>
              
              <Text style={styles.transactionStatus}>
                Status: {getStatusText(transaction.status)}
              </Text>
              
              <Text style={styles.transactionDate}>
                {new Date(transaction.created_at).toLocaleDateString('uz-UZ')}
              </Text>
              
              {transaction.description && (
                <Text style={styles.transactionDescription}>
                  {transaction.description}
                </Text>
              )}
            </View>
          ))
        )}
      </View>
    </ScrollView>
  );
}

function getStatusText(status: string): string {
  const statusMap: { [key: string]: string } = {
    pending: '? Kutilmoqda',
    processing: '?? Jarayonda',
    completed: '? Bajarildi',
    failed: '? Xato',
  };
  return statusMap[status] || status;
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
  balanceCard: {
    backgroundColor: '#007bff',
    margin: 15,
    padding: 25,
    borderRadius: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 6,
    elevation: 5,
  },
  balanceLabel: {
    color: '#e0e0e0',
    fontSize: 14,
    marginBottom: 5,
  },
  balanceAmount: {
    color: '#fff',
    fontSize: 42,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  trafficInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  trafficItem: {
    flex: 1,
  },
  trafficLabel: {
    color: '#e0e0e0',
    fontSize: 12,
    marginBottom: 3,
  },
  trafficValue: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  buttonRow: {
    flexDirection: 'row',
    gap: 10,
  },
  refreshButton: {
    flex: 1,
    backgroundColor: 'rgba(255,255,255,0.2)',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  refreshButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  withdrawButton: {
    flex: 1,
    backgroundColor: '#ffc107',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  withdrawButtonDisabled: {
    backgroundColor: '#ccc',
  },
  withdrawButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  section: {
    margin: 15,
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
    color: '#999',
    fontSize: 14,
  },
  transactionCard: {
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
  transactionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  transactionType: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  transactionAmount: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  incomeAmount: {
    color: '#28a745',
  },
  withdrawAmount: {
    color: '#dc3545',
  },
  transactionStatus: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  transactionDate: {
    fontSize: 11,
    color: '#999',
  },
  transactionDescription: {
    fontSize: 12,
    color: '#666',
    marginTop: 8,
    fontStyle: 'italic',
  },
});
