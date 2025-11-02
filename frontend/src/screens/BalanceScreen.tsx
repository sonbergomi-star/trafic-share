import React, { useEffect, useState } from 'react';
import { View, StyleSheet, Text, TouchableOpacity, FlatList } from 'react-native';
import Toast from 'react-native-toast-message';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useNavigation } from '@react-navigation/native';

import { BalanceApi } from '../api/endpoints';
import { useAuth } from '../context/AuthContext';
import { BalanceOverview, Transaction } from '../types/api';
import { SectionCard } from '../components/SectionCard';
import { Loader } from '../components/Loader';
import { formatCurrency, formatMb, utcToLocal } from '../utils/format';
import { BalanceStackParamList } from '../navigation/AppNavigator';

type NavigationProp = NativeStackNavigationProp<BalanceStackParamList, 'BalanceHome'>;

const BalanceScreen = () => {
  const navigation = useNavigation<NavigationProp>();
  const { user } = useAuth();
  const [overview, setOverview] = useState<BalanceOverview | null>(null);
  const [loading, setLoading] = useState(false);

  const loadData = async () => {
    if (!user) return;
    try {
      setLoading(true);
      const response = await BalanceApi.overview(user.telegram_id);
      setOverview(response.data);
    } catch (error) {
      Toast.show({ type: 'error', text1: 'Balans ma?lumotlari olinmadi' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [user?.telegram_id]);

  return (
    <View style={styles.container}>
      <Loader visible={loading} />
      {overview && (
        <>
          <SectionCard>
            <Text style={styles.title}>?? Umumiy balans</Text>
            <Text style={styles.balance}>{formatCurrency(overview.balance_usd)}</Text>
            <Text style={styles.sub}>Bugungi daromad: {formatCurrency(overview.today_earn)}</Text>
            <Text style={styles.sub}>Oy boshidan: {formatCurrency(overview.month_earn)}</Text>
            <Text style={styles.sub}>Yuborilgan trafik: {formatMb(overview.sent_mb)}</Text>
            <Text style={styles.sub}>Sotilgan trafik: {formatMb(overview.used_mb)}</Text>
            <TouchableOpacity style={styles.withdrawBtn} onPress={() => navigation.navigate('Withdraw')}>
              <Text style={styles.withdrawLabel}>Pul yechish</Text>
            </TouchableOpacity>
          </SectionCard>

          <SectionCard>
            <Text style={styles.title}>Oxirgi tranzaktsiyalar</Text>
            <FlatList
              data={overview.transactions.slice(0, 5)}
              keyExtractor={item => item.id.toString()}
              renderItem={({ item }) => <TransactionRow transaction={item} />}
              ItemSeparatorComponent={() => <View style={styles.separator} />}
              scrollEnabled={false}
            />
            <TouchableOpacity style={styles.refreshBtn} onPress={loadData}>
              <Text style={styles.refreshLabel}>Yangilash</Text>
            </TouchableOpacity>
          </SectionCard>
        </>
      )}
    </View>
  );
};

const TransactionRow: React.FC<{ transaction: Transaction }> = ({ transaction }) => {
  return (
    <View style={styles.transactionRow}>
      <View>
        <Text style={styles.transactionType}>{transaction.type.toUpperCase()}</Text>
        <Text style={styles.transactionDate}>{utcToLocal(transaction.created_at)}</Text>
      </View>
      <Text style={[styles.transactionAmount, { color: transaction.amount_usd >= 0 ? '#4ade80' : '#f87171' }]}>
        {formatCurrency(transaction.amount_usd)}
      </Text>
    </View>
  );
};

export default BalanceScreen;

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
    color: '#e2e8f0',
    marginBottom: 8,
  },
  balance: {
    fontSize: 32,
    fontWeight: '700',
    color: '#38bdf8',
    marginBottom: 8,
  },
  sub: {
    color: '#94a3b8',
    marginBottom: 4,
  },
  withdrawBtn: {
    backgroundColor: '#22c55e',
    borderRadius: 14,
    paddingVertical: 12,
    alignItems: 'center',
    marginTop: 16,
  },
  withdrawLabel: {
    color: '#052e16',
    fontWeight: '700',
    fontSize: 16,
  },
  transactionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  transactionType: {
    color: '#f8fafc',
    fontWeight: '600',
  },
  transactionDate: {
    color: '#64748b',
    fontSize: 12,
  },
  transactionAmount: {
    fontWeight: '700',
  },
  separator: {
    height: 1,
    backgroundColor: '#1e293b',
  },
  refreshBtn: {
    marginTop: 16,
    alignItems: 'center',
    paddingVertical: 10,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#1d4ed8',
  },
  refreshLabel: {
    color: '#93c5fd',
    fontWeight: '600',
  },
});

