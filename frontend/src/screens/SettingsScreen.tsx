import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Switch,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { API } from '../api/client';

export default function SettingsScreen() {
  const [loading, setLoading] = useState(true);
  const [settings, setSettings] = useState<any>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const userData = await AsyncStorage.getItem('user_data');
      if (userData) {
        const user = JSON.parse(userData);
        const response = await API.getSettings(user.telegram_id);
        setSettings(response.data);
      }
    } catch (error) {
      console.error('Load settings error:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateSetting = async (key: string, value: any) => {
    // Update local state immediately
    setSettings({ ...settings, [key]: value });

    // Save to backend
    try {
      const userData = await AsyncStorage.getItem('user_data');
      if (userData) {
        const user = JSON.parse(userData);
        await API.updateSettings(user.telegram_id, { [key]: value });
      }
    } catch (error) {
      console.error('Update setting error:', error);
      Alert.alert('Xato', 'Sozlamani saqlashda xatolik');
      // Revert on error
      loadSettings();
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007bff" />
      </View>
    );
  }

  if (!settings) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Sozlamalar yuklanmadi</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {/* Language Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Til / Language</Text>

        <View style={styles.card}>
          <TouchableOpacity
            style={styles.languageOption}
            onPress={() => updateSetting('language', 'uz')}
          >
            <View style={styles.languageOptionContent}>
              <Text style={styles.languageText}>???? O'zbek</Text>
            </View>
            {settings.language === 'uz' && (
              <Icon name="check-circle" size={24} color="#28a745" />
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.languageOption}
            onPress={() => updateSetting('language', 'ru')}
          >
            <View style={styles.languageOptionContent}>
              <Text style={styles.languageText}>???? ???????</Text>
            </View>
            {settings.language === 'ru' && (
              <Icon name="check-circle" size={24} color="#28a745" />
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.languageOption}
            onPress={() => updateSetting('language', 'en')}
          >
            <View style={styles.languageOptionContent}>
              <Text style={styles.languageText}>???? English</Text>
            </View>
            {settings.language === 'en' && (
              <Icon name="check-circle" size={24} color="#28a745" />
            )}
          </TouchableOpacity>
        </View>
      </View>

      {/* Notifications Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Bildirishnomalar</Text>

        <View style={styles.card}>
          <View style={styles.settingRow}>
            <View style={styles.settingContent}>
              <Icon name="bell" size={24} color="#007bff" />
              <View style={styles.settingText}>
                <Text style={styles.settingTitle}>Push notification</Text>
                <Text style={styles.settingSubtitle}>
                  Barcha bildirishnomalar
                </Text>
              </View>
            </View>
            <Switch
              value={settings.push_notifications}
              onValueChange={(value) =>
                updateSetting('push_notifications', value)
              }
              trackColor={{ false: '#ccc', true: '#007bff' }}
            />
          </View>

          <View style={styles.settingRow}>
            <View style={styles.settingContent}>
              <Icon name="information" size={24} color="#007bff" />
              <View style={styles.settingText}>
                <Text style={styles.settingTitle}>Sessiya yangiliklari</Text>
                <Text style={styles.settingSubtitle}>
                  Trafik sessiyalari haqida
                </Text>
              </View>
            </View>
            <Switch
              value={settings.session_updates}
              onValueChange={(value) => updateSetting('session_updates', value)}
              trackColor={{ false: '#ccc', true: '#007bff' }}
            />
          </View>

          <View style={styles.settingRow}>
            <View style={styles.settingContent}>
              <Icon name="update" size={24} color="#007bff" />
              <View style={styles.settingText}>
                <Text style={styles.settingTitle}>Tizim yangiliklari</Text>
                <Text style={styles.settingSubtitle}>
                  Yangiliklar va e'lonlar
                </Text>
              </View>
            </View>
            <Switch
              value={settings.system_updates}
              onValueChange={(value) => updateSetting('system_updates', value)}
              trackColor={{ false: '#ccc', true: '#007bff' }}
            />
          </View>
        </View>
      </View>

      {/* App Settings */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Ilova sozlamalari</Text>

        <View style={styles.card}>
          <View style={styles.settingRow}>
            <View style={styles.settingContent}>
              <Icon name="battery-heart" size={24} color="#28a745" />
              <View style={styles.settingText}>
                <Text style={styles.settingTitle}>Battery Saver</Text>
                <Text style={styles.settingSubtitle}>
                  Quvvat tejash rejimi
                </Text>
              </View>
            </View>
            <Switch
              value={settings.battery_saver}
              onValueChange={(value) => updateSetting('battery_saver', value)}
              trackColor={{ false: '#ccc', true: '#28a745' }}
            />
          </View>

          <View style={styles.settingRow}>
            <View style={styles.settingContent}>
              <Icon name="theme-light-dark" size={24} color="#666" />
              <View style={styles.settingText}>
                <Text style={styles.settingTitle}>Tema</Text>
                <Text style={styles.settingSubtitle}>
                  {settings.theme === 'light' ? 'Yorug\'' : 'Qorong\'u'}
                </Text>
              </View>
            </View>
            <TouchableOpacity
              onPress={() =>
                updateSetting(
                  'theme',
                  settings.theme === 'light' ? 'dark' : 'light'
                )
              }
            >
              <Icon
                name={
                  settings.theme === 'light'
                    ? 'weather-sunny'
                    : 'weather-night'
                }
                size={24}
                color={settings.theme === 'light' ? '#FDB813' : '#5A5A8F'}
              />
            </TouchableOpacity>
          </View>
        </View>
      </View>

      {/* About Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Ma'lumot</Text>

        <View style={styles.card}>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Ilova versiyasi</Text>
            <Text style={styles.infoValue}>1.0.0</Text>
          </View>

          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>API Server</Text>
            <Text style={styles.infoValue}>113.30.191.89</Text>
          </View>
        </View>
      </View>

      {/* Footer */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>
          ? 2024 Traffic Sharing Platform
        </Text>
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
  section: {
    margin: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  languageOption: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 15,
    paddingHorizontal: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  languageOptionContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  languageText: {
    fontSize: 16,
    color: '#333',
  },
  settingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
    paddingHorizontal: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  settingContent: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  settingText: {
    marginLeft: 15,
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  settingSubtitle: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 12,
    paddingHorizontal: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  infoLabel: {
    fontSize: 14,
    color: '#666',
  },
  infoValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  footer: {
    alignItems: 'center',
    paddingVertical: 30,
  },
  footerText: {
    fontSize: 11,
    color: '#999',
  },
});
