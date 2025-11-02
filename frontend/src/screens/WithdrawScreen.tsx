import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ScrollView,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API } from '../api/client';

export default function WithdrawScreen({ navigation }: any) {
  const [amount, setAmount] = useState('');
  const [walletAddress, setWalletAddress] = useState('');
  const [loading, setLoading] = useState(false);

  const handleWithdraw = async () => {
    if (!amount || !walletAddress) {
      Alert.alert('Xato', 'Barcha maydonlarni to\'ldiring');
      return;
    }

    const amountNum = parseFloat(amount);
    if (isNaN(amountNum) || amountNum < 1.39) {
      Alert.alert('Xato', 'Minimal yechish summasi $1.39');
      return;
    }

    setLoading(true);
    try {
      const userData = await AsyncStorage.getItem('user_data');
      if (userData) {
        const user = JSON.parse(userData);
        
        const response = await API.createWithdraw({
          telegram_id: user.telegram_id,
          amount_usd: amountNum,
          wallet_address: walletAddress,
          network: 'BEP20',
        });

        Alert.alert(
          'Muvaffaqiyat',
          'Yechish so\'rovi yaratildi. Tez orada mablag\' hisobingizga tushadi.',
          [{ text: 'OK', onPress: () => navigation.goBack() }]
        );
      }
    } catch (error: any) {
      Alert.alert(
        'Xato',
        error.response?.data?.detail || 'Yechishda xatolik yuz berdi'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Pul yechish (USDT BEP20)</Text>
        
        <View style={styles.infoBox}>
          <Text style={styles.infoText}>?? Minimal: $1.39</Text>
          <Text style={styles.infoText}>?? Maksimal: $100.00</Text>
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Summa (USD)</Text>
          <TextInput
            style={styles.input}
            placeholder="Masalan: 5.00"
            keyboardType="decimal-pad"
            value={amount}
            onChangeText={setAmount}
          />
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>BEP20 Wallet Address</Text>
          <TextInput
            style={styles.input}
            placeholder="0x..."
            value={walletAddress}
            onChangeText={setWalletAddress}
            autoCapitalize="none"
          />
        </View>

        <TouchableOpacity
          style={[styles.submitButton, loading && styles.submitButtonDisabled]}
          onPress={handleWithdraw}
          disabled={loading}
        >
          <Text style={styles.submitButtonText}>
            {loading ? 'Yuborilmoqda...' : 'Pulni yechish'}
          </Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 20,
  },
  infoBox: {
    backgroundColor: '#e3f2fd',
    padding: 15,
    borderRadius: 10,
    marginBottom: 20,
  },
  infoText: {
    fontSize: 14,
    color: '#1976d2',
    marginBottom: 5,
  },
  formGroup: {
    marginBottom: 20,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  submitButton: {
    backgroundColor: '#ffc107',
    paddingVertical: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 10,
  },
  submitButtonDisabled: {
    backgroundColor: '#ccc',
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
