import React, { useState } from 'react';
import { View, StyleSheet, Text, TextInput, TouchableOpacity } from 'react-native';
import Toast from 'react-native-toast-message';

import { useAuth } from '../context/AuthContext';
import { BalanceApi } from '../api/endpoints';

const WithdrawScreen = () => {
  const { user } = useAuth();
  const [amount, setAmount] = useState('5.00');
  const [wallet, setWallet] = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!user) return;
    if (!wallet.startsWith('0x') || wallet.length !== 42) {
      Toast.show({ type: 'error', text1: 'Wallet BEP20 formatida bo?lishi kerak' });
      return;
    }
    try {
      setLoading(true);
      await BalanceApi.withdraw({ telegram_id: user.telegram_id, amount_usd: Number(amount), wallet_address: wallet, network: 'BEP20' });
      Toast.show({ type: 'success', text1: 'Yechish so?rovi yuborildi' });
    } catch (error) {
      Toast.show({ type: 'error', text1: 'So?rov yuborilmadi' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>?? USDT (BEP20) yechish</Text>
      <Text style={styles.help}>Minimal yechish: $1.39 | Maksimal: $100.00</Text>
      <View style={styles.formGroup}>
        <Text style={styles.label}>Miqdor (USD)</Text>
        <TextInput
          style={styles.input}
          keyboardType="decimal-pad"
          value={amount}
          onChangeText={setAmount}
          placeholder="$5.00"
        />
      </View>
      <View style={styles.formGroup}>
        <Text style={styles.label}>BEP20 USDT manzil</Text>
        <TextInput
          style={styles.input}
          value={wallet}
          onChangeText={setWallet}
          placeholder="0x..."
          autoCapitalize="none"
        />
      </View>
      <TouchableOpacity style={[styles.button, loading && { opacity: 0.6 }]} onPress={submit} disabled={loading}>
        <Text style={styles.buttonLabel}>{loading ? 'Yuborilmoqda...' : 'Pul yechish'}</Text>
      </TouchableOpacity>
      <View style={styles.notice}>
        <Text style={styles.noticeText}>? So?rov yuborilgach, holatini ?Balans? sahifasidan kuzatishingiz mumkin.</Text>
      </View>
    </View>
  );
};

export default WithdrawScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#050912',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: '#f8fafc',
    marginBottom: 8,
  },
  help: {
    color: '#94a3b8',
    marginBottom: 20,
  },
  formGroup: {
    marginBottom: 16,
  },
  label: {
    color: '#cbd5f5',
    marginBottom: 6,
  },
  input: {
    backgroundColor: '#101727',
    borderRadius: 12,
    padding: 14,
    color: '#f8fafc',
  },
  button: {
    backgroundColor: '#22c55e',
    borderRadius: 14,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: 12,
  },
  buttonLabel: {
    color: '#052e16',
    fontWeight: '700',
    fontSize: 16,
  },
  notice: {
    marginTop: 20,
    padding: 12,
    backgroundColor: '#0f172a',
    borderRadius: 12,
  },
  noticeText: {
    color: '#94a3b8',
  },
});

