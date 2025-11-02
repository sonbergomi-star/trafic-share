import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API } from '../api/client';

export default function TelegramAuthScreen({ navigation }: any) {
  const [loading, setLoading] = useState(false);

  const handleTelegramAuth = async () => {
    setLoading(true);
    
    try {
      // Mock Telegram auth data (in real app, use Telegram SDK)
      const mockTelegramData = {
        id: 599382114,
        first_name: 'User',
        username: 'testuser',
        photo_url: null,
        auth_date: Math.floor(Date.now() / 1000),
        hash: 'mock_hash',
      };

      const response = await API.telegramAuth(mockTelegramData);
      
      if (response.data.status === 'success') {
        await AsyncStorage.setItem('jwt_token', response.data.token);
        await AsyncStorage.setItem('user_data', JSON.stringify(response.data.user));
        
        // Navigate to main app
        navigation.replace('Main');
      }
    } catch (error: any) {
      Alert.alert('Xato', error.response?.data?.detail || 'Login xatosi');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Traffic Sharing Platform</Text>
        <Text style={styles.subtitle}>
          Telegram orqali tizimga kiring
        </Text>

        <TouchableOpacity
          style={styles.loginButton}
          onPress={handleTelegramAuth}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <>
              <Text style={styles.loginButtonText}>
                ?? Login with Telegram
              </Text>
            </>
          )}
        </TouchableOpacity>

        <View style={styles.footer}>
          <Text style={styles.footerText}>
            ? ToS & Privacy Policy ga roziman
          </Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    width: '80%',
    alignItems: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 40,
    textAlign: 'center',
  },
  loginButton: {
    backgroundColor: '#0088cc',
    paddingVertical: 15,
    paddingHorizontal: 40,
    borderRadius: 25,
    width: '100%',
    alignItems: 'center',
  },
  loginButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
  footer: {
    marginTop: 30,
  },
  footerText: {
    color: '#666',
    fontSize: 12,
  },
});
