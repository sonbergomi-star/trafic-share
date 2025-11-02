import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import { useAuth } from '../hooks/useAuth';
import { api } from '../services/api';

interface WithdrawHistory {
  id: number;
  amount_usd: number;
  wallet_address: string;
  status: string;
  created_at: string;
  tx_hash?: string;
}

/**
 * REAL Withdraw screen with USDT BEP20 support
 */
export const WithdrawScreen: React.FC = () => {
  const { user } = useAuth();
  
  const [balance, setBalance] = useState(0);
  const [amount, setAmount] = useState('');
  const [walletAddress, setWalletAddress] = useState('');
  const [isConfirmed, setIsConfirmed] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [history, setHistory] = useState<WithdrawHistory[]>([]);

  const MIN_WITHDRAW = 1.39;
  const MAX_WITHDRAW = 100.00;

  // Load balance and history
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      // Load balance
      const balanceRes = await api.get(`/user/balance/${user?.telegram_id}`);
      setBalance(balanceRes.data.balance.usd);
      
      // Load withdraw history
      const historyRes = await api.get('/withdraws', {
        params: { limit: 5 }
      });
      setHistory(historyRes.data.data || []);
    } catch (error) {
      console.error('? Failed to load data:', error);
    }
  };

  // Validate wallet address (BEP20)
  const validateAddress = (address: string): boolean => {
    const bep20Regex = /^0x[a-fA-F0-9]{40}$/;
    return bep20Regex.test(address);
  };

  // Handle withdraw
  const handleWithdraw = async () => {
    // Validate amount
    const amountNum = parseFloat(amount);
    
    if (isNaN(amountNum) || amountNum < MIN_WITHDRAW) {
      Alert.alert('? Xato', `Minimal yechish summasi: $${MIN_WITHDRAW}`);
      return;
    }
    
    if (amountNum > balance) {
      Alert.alert('? Xato', 'Balansingizda yetarli mablag\' yo\'q');
      return;
    }
    
    if (amountNum > MAX_WITHDRAW) {
      Alert.alert('? Xato', `Maksimal yechish summasi: $${MAX_WITHDRAW}`);
      return;
    }
    
    // Validate wallet address
    if (!validateAddress(walletAddress)) {
      Alert.alert(
        '? Xato',
        'BEP20 manzili noto\'g\'ri. Manzil 0x bilan boshlanishi va 42 belgidan iborat bo\'lishi kerak.'
      );
      return;
    }
    
    // Check confirmation
    if (!isConfirmed) {
      Alert.alert('? Xato', 'Iltimos, manzil to\'g\'riligini tasdiqlang');
      return;
    }

    // Confirm withdrawal
    Alert.alert(
      '?? Tasdiqlash',
      `$${amountNum.toFixed(2)} yechishni xohlaysizmi?\n\nManzil: ${walletAddress}`,
      [
        { text: 'Yo\'q', style: 'cancel' },
        {
          text: 'Ha, yechish',
          onPress: async () => {
            setIsLoading(true);
            
            try {
              const response = await api.post('/withdraw', {
                telegram_id: user?.telegram_id,
                amount_usd: amountNum,
                wallet_address: walletAddress,
                network: 'BEP20',
              });
              
              if (response.data.status === 'pending') {
                Alert.alert(
                  '? Muvaffaqiyatli',
                  'Yechish so\'rovi qabul qilindi! To\'lov tez orada amalga oshiriladi.',
                  [{ text: 'OK', onPress: () => {
                    setAmount('');
                    setWalletAddress('');
                    setIsConfirmed(false);
                    loadData();
                  }}]
                );
              }
            } catch (error: any) {
              const errorMsg = error.response?.data?.detail || 'Xatolik yuz berdi';
              Alert.alert('? Xato', errorMsg);
            } finally {
              setIsLoading(false);
            }
          },
        },
      ]
    );
  };

  const getStatusEmoji = (status: string) => {
    switch (status) {
      case 'completed': return '?';
      case 'pending': return '?';
      case 'processing': return '??';
      case 'failed': return '?';
      default: return '?';
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Balance Card */}
        <LinearGradient
          colors={['#6A1B9A', '#8E24AA', '#AB47BC']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={styles.balanceCard}
        >
          <Text style={styles.balanceLabel}>?? Joriy balans</Text>
          <Text style={styles.balanceAmount}>${balance.toFixed(2)}</Text>
          <Text style={styles.balanceHint}>
            Minimal: ${MIN_WITHDRAW} ? Maksimal: ${MAX_WITHDRAW}
          </Text>
        </LinearGradient>

        {/* Withdraw Form */}
        <View style={styles.formCard}>
          <Text style={styles.formTitle}>?? Pul yechish (USDT BEP20)</Text>
          
          {/* Amount Input */}
          <View style={styles.inputGroup}>
            <Text style={styles.inputLabel}>?? Summa (USD)</Text>
            <TextInput
              style={styles.input}
              placeholder="5.00"
              placeholderTextColor="#666"
              keyboardType="decimal-pad"
              value={amount}
              onChangeText={setAmount}
            />
          </View>

          {/* Wallet Address Input */}
          <View style={styles.inputGroup}>
            <Text style={styles.inputLabel}>?? BEP20 Manzili</Text>
            <TextInput
              style={styles.input}
              placeholder="0x..."
              placeholderTextColor="#666"
              value={walletAddress}
              onChangeText={setWalletAddress}
              autoCapitalize="none"
            />
          </View>

          {/* Confirmation Checkbox */}
          <TouchableOpacity
            style={styles.checkbox}
            onPress={() => setIsConfirmed(!isConfirmed)}
          >
            <View style={[styles.checkboxBox, isConfirmed && styles.checkboxBoxChecked]}>
              {isConfirmed && <Text style={styles.checkboxCheck}>?</Text>}
            </View>
            <Text style={styles.checkboxLabel}>
              Men BEP20 manzilini to'g'ri kiritganimni tasdiqlayapman
            </Text>
          </TouchableOpacity>

          {/* Withdraw Button */}
          <TouchableOpacity
            style={styles.withdrawButton}
            onPress={handleWithdraw}
            disabled={isLoading}
          >
            <LinearGradient
              colors={['#4CAF50', '#45A049']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
              style={styles.withdrawButtonGradient}
            >
              {isLoading ? (
                <ActivityIndicator color="#FFF" />
              ) : (
                <Text style={styles.withdrawButtonText}>?? PULNI YECHISH</Text>
              )}
            </LinearGradient>
          </TouchableOpacity>
        </View>

        {/* Withdraw History */}
        <View style={styles.historyCard}>
          <Text style={styles.historyTitle}>?? Yechish tarixi</Text>
          
          {history.length === 0 ? (
            <Text style={styles.emptyText}>Hozircha yechish tarixi yo'q</Text>
          ) : (
            history.map((item) => (
              <View key={item.id} style={styles.historyItem}>
                <View style={styles.historyItemLeft}>
                  <Text style={styles.historyStatus}>
                    {getStatusEmoji(item.status)} {item.status}
                  </Text>
                  <Text style={styles.historyDate}>
                    {new Date(item.created_at).toLocaleDateString('uz-UZ')}
                  </Text>
                </View>
                <View style={styles.historyItemRight}>
                  <Text style={styles.historyAmount}>
                    ${item.amount_usd.toFixed(2)}
                  </Text>
                  {item.tx_hash && (
                    <Text style={styles.historyTxHash} numberOfLines={1}>
                      TX: {item.tx_hash.substring(0, 10)}...
                    </Text>
                  )}
                </View>
              </View>
            ))
          )}
        </View>
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
  balanceCard: {
    borderRadius: 20,
    padding: 24,
    marginBottom: 20,
    elevation: 8,
  },
  balanceLabel: {
    fontSize: 16,
    color: '#FFF',
    marginBottom: 8,
  },
  balanceAmount: {
    fontSize: 42,
    color: '#FFF',
    fontWeight: 'bold',
    marginBottom: 8,
  },
  balanceHint: {
    fontSize: 12,
    color: '#EEE',
  },
  formCard: {
    backgroundColor: '#1E1E1E',
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
  },
  formTitle: {
    fontSize: 20,
    color: '#FFF',
    fontWeight: 'bold',
    marginBottom: 20,
  },
  inputGroup: {
    marginBottom: 16,
  },
  inputLabel: {
    fontSize: 14,
    color: '#AAA',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#2A2A2A',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    color: '#FFF',
  },
  checkbox: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  checkboxBox: {
    width: 24,
    height: 24,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: '#666',
    marginRight: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkboxBoxChecked: {
    backgroundColor: '#4CAF50',
    borderColor: '#4CAF50',
  },
  checkboxCheck: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  checkboxLabel: {
    flex: 1,
    fontSize: 14,
    color: '#AAA',
  },
  withdrawButton: {
    borderRadius: 12,
    overflow: 'hidden',
  },
  withdrawButtonGradient: {
    paddingVertical: 16,
    alignItems: 'center',
  },
  withdrawButtonText: {
    fontSize: 18,
    color: '#FFF',
    fontWeight: 'bold',
  },
  historyCard: {
    backgroundColor: '#1E1E1E',
    borderRadius: 16,
    padding: 20,
  },
  historyTitle: {
    fontSize: 18,
    color: '#FFF',
    fontWeight: 'bold',
    marginBottom: 16,
  },
  emptyText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    paddingVertical: 20,
  },
  historyItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#2A2A2A',
  },
  historyItemLeft: {
    flex: 1,
  },
  historyStatus: {
    fontSize: 14,
    color: '#FFF',
    marginBottom: 4,
  },
  historyDate: {
    fontSize: 12,
    color: '#666',
  },
  historyItemRight: {
    alignItems: 'flex-end',
  },
  historyAmount: {
    fontSize: 16,
    color: '#4CAF50',
    fontWeight: 'bold',
    marginBottom: 4,
  },
  historyTxHash: {
    fontSize: 11,
    color: '#666',
    width: 100,
  },
});
