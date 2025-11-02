import React, { useCallback, useMemo, useState } from 'react';
import { View, StyleSheet, Text, ActivityIndicator } from 'react-native';
import { WebView, WebViewMessageEvent } from 'react-native-webview';
import Constants from 'expo-constants';

import { AuthApi } from '../api/endpoints';
import { useAuth } from '../context/AuthContext';
import { AuthResponse } from '../types/api';
import { Loader } from '../components/Loader';

const extra = Constants?.expoConfig?.extra || Constants?.manifest?.extra || {};

const AuthScreen = () => {
  const { login } = useAuth();
  const [loading, setLoading] = useState(false);

  const widgetHtml = useMemo(() => {
    const bot = extra?.telegramBot || 'your_bot_username';
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style>
          body { background-color: #050912; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; }
        </style>
      </head>
      <body>
        <script async src="https://telegram.org/js/telegram-widget.js?22"
          data-telegram-login="${bot}"
          data-size="large"
          data-userpic="false"
          data-radius="8"
          data-request-access="write"
          data-onauth="onTelegramAuth">
        </script>
        <script>
          function onTelegramAuth(user) {
            if (window.ReactNativeWebView) {
              window.ReactNativeWebView.postMessage(JSON.stringify(user));
            }
          }
        </script>
      </body>
      </html>
    `;
  }, []);

  const handleAuth = useCallback(
    async (event: WebViewMessageEvent) => {
      try {
        setLoading(true);
        const data = JSON.parse(event.nativeEvent.data);
        const response = await AuthApi.telegramLogin(data);
        await login(response.data as AuthResponse);
      } catch (error) {
        console.warn('[Auth]', error);
      } finally {
        setLoading(false);
      }
    },
    [login],
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>?? Telegram orqali kirish</Text>
      <Text style={styles.subtitle}>?Login with Telegram? tugmasini bosing va tizimga kiring.</Text>
      <View style={styles.card}>
        <WebView
          source={{ html: widgetHtml }}
          style={styles.webview}
          onMessage={handleAuth}
          originWhitelist={["*"]}
          startInLoadingState
          renderLoading={() => (
            <View style={styles.webviewLoader}>
              <ActivityIndicator color="#4ade80" />
            </View>
          )}
        />
      </View>
      <Text style={styles.terms}>Davom etish orqali siz foydalanish shartlari va maxfiylik siyosatiga rozilik bildirasiz.</Text>
      <Loader visible={loading} />
    </View>
  );
};

export default AuthScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#050912',
    paddingTop: 80,
    paddingHorizontal: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#f8fafc',
    marginBottom: 12,
  },
  subtitle: {
    fontSize: 16,
    color: '#cbd5f5',
    marginBottom: 24,
  },
  card: {
    backgroundColor: '#101727',
    borderRadius: 20,
    padding: 16,
    shadowColor: '#000',
    shadowOpacity: 0.25,
    shadowRadius: 16,
    shadowOffset: { width: 0, height: 12 },
    elevation: 8,
  },
  webview: {
    height: 200,
    borderRadius: 12,
    overflow: 'hidden',
  },
  webviewLoader: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  terms: {
    marginTop: 24,
    color: '#64748b',
    fontSize: 13,
    textAlign: 'center',
  },
});

