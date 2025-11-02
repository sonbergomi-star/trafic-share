import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  Image,
  Alert,
  ActivityIndicator,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { API } from '../api/client';

export default function ProfileScreen({ navigation }: any) {
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<any>(null);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const userData = await AsyncStorage.getItem('user_data');
      if (userData) {
        const user = JSON.parse(userData);
        const response = await API.getProfile(user.telegram_id);
        setProfile(response.data);
      }
    } catch (error) {
      console.error('Load profile error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRenewToken = async () => {
    Alert.alert(
      'Token yangilash',
      'JWT tokeningizni yangilashni xohlaysizmi?',
      [
        { text: 'Bekor qilish', style: 'cancel' },
        {
          text: 'Yangilash',
          onPress: async () => {
            try {
              const userData = await AsyncStorage.getItem('user_data');
              if (userData) {
                const user = JSON.parse(userData);
                const response = await API.renewToken(user.telegram_id);
                await AsyncStorage.setItem('jwt_token', response.data.jwt_token);
                Alert.alert('Muvaffaqiyat', 'Token yangilandi');
              }
            } catch (error) {
              Alert.alert('Xato', 'Token yangilashda xatolik');
            }
          },
        },
      ]
    );
  };

  const handleLogout = async () => {
    Alert.alert(
      'Hisobdan chiqish',
      'Hisobdan chiqishni xohlaysizmi?',
      [
        { text: 'Bekor qilish', style: 'cancel' },
        {
          text: 'Chiqish',
          style: 'destructive',
          onPress: async () => {
            try {
              const userData = await AsyncStorage.getItem('user_data');
              if (userData) {
                const user = JSON.parse(userData);
                await API.logout(user.telegram_id);
              }
              
              await AsyncStorage.removeItem('jwt_token');
              await AsyncStorage.removeItem('user_data');
              
              navigation.reset({
                index: 0,
                routes: [{ name: 'Auth' }],
              });
            } catch (error) {
              console.error('Logout error:', error);
            }
          },
        },
      ]
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007bff" />
      </View>
    );
  }

  if (!profile) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Profil yuklanmadi</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {/* Profile Header */}
      <View style={styles.header}>
        {profile.photo_url ? (
          <Image source={{ uri: profile.photo_url }} style={styles.avatar} />
        ) : (
          <View style={styles.avatarPlaceholder}>
            <Icon name="account" size={60} color="#fff" />
          </View>
        )}
        <Text style={styles.name}>{profile.first_name}</Text>
        <Text style={styles.username}>@{profile.username}</Text>
      </View>

      {/* Profile Info */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Hisob ma'lumotlari</Text>

        <View style={styles.infoCard}>
          <View style={styles.infoRow}>
            <Icon name="identifier" size={20} color="#666" />
            <Text style={styles.infoLabel}>Telegram ID:</Text>
            <Text style={styles.infoValue}>{profile.telegram_id}</Text>
          </View>

          <View style={styles.infoRow}>
            <Icon name="clock-outline" size={20} color="#666" />
            <Text style={styles.infoLabel}>So'nggi kirish:</Text>
            <Text style={styles.infoValue}>
              {profile.auth_date
                ? new Date(profile.auth_date).toLocaleDateString('uz-UZ')
                : 'N/A'}
            </Text>
          </View>

          {profile.last_login_device && (
            <View style={styles.infoRow}>
              <Icon name="cellphone" size={20} color="#666" />
              <Text style={styles.infoLabel}>Qurilma:</Text>
              <Text style={styles.infoValue}>{profile.last_login_device}</Text>
            </View>
          )}

          {profile.last_login_ip && (
            <View style={styles.infoRow}>
              <Icon name="ip" size={20} color="#666" />
              <Text style={styles.infoLabel}>IP:</Text>
              <Text style={styles.infoValue}>{profile.last_login_ip}</Text>
            </View>
          )}
        </View>
      </View>

      {/* Security Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Xavfsizlik</Text>

        <View style={styles.securityCard}>
          <View style={styles.securityRow}>
            <Icon name="shield-check" size={24} color="#28a745" />
            <View style={styles.securityContent}>
              <Text style={styles.securityTitle}>2FA</Text>
              <Text style={styles.securitySubtitle}>
                {profile.two_factor_enabled ? 'Faol' : 'Faol emas'}
              </Text>
            </View>
            <Icon
              name={profile.two_factor_enabled ? 'check-circle' : 'close-circle'}
              size={24}
              color={profile.two_factor_enabled ? '#28a745' : '#999'}
            />
          </View>

          <TouchableOpacity
            style={styles.securityRow}
            onPress={handleRenewToken}
          >
            <Icon name="key-variant" size={24} color="#007bff" />
            <View style={styles.securityContent}>
              <Text style={styles.securityTitle}>JWT Token</Text>
              <Text style={styles.securitySubtitle}>Tokenni yangilash</Text>
            </View>
            <Icon name="chevron-right" size={24} color="#999" />
          </TouchableOpacity>
        </View>
      </View>

      {/* Actions */}
      <View style={styles.section}>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('Settings')}
        >
          <Icon name="cog" size={24} color="#007bff" />
          <Text style={styles.actionButtonText}>Sozlamalar</Text>
          <Icon name="chevron-right" size={24} color="#999" />
        </TouchableOpacity>

        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Icon name="logout" size={24} color="#dc3545" />
          <Text style={styles.logoutButtonText}>Hisobdan chiqish</Text>
        </TouchableOpacity>
      </View>

      {/* App Info */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>Traffic Sharing Platform</Text>
        <Text style={styles.footerVersion}>v1.0.0</Text>
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
  header: {
    backgroundColor: '#007bff',
    paddingVertical: 40,
    alignItems: 'center',
  },
  avatar: {
    width: 100,
    height: 100,
    borderRadius: 50,
    borderWidth: 3,
    borderColor: '#fff',
  },
  avatarPlaceholder: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#0056b3',
    justifyContent: 'center',
    alignItems: 'center',
  },
  name: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 15,
  },
  username: {
    fontSize: 16,
    color: '#e0e0e0',
    marginTop: 5,
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
  infoCard: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  infoLabel: {
    flex: 1,
    fontSize: 14,
    color: '#666',
    marginLeft: 10,
  },
  infoValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  securityCard: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  securityRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  securityContent: {
    flex: 1,
    marginLeft: 15,
  },
  securityTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  securitySubtitle: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  actionButton: {
    backgroundColor: '#fff',
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  actionButtonText: {
    flex: 1,
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginLeft: 15,
  },
  logoutButton: {
    backgroundColor: '#fff',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 15,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#dc3545',
  },
  logoutButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#dc3545',
    marginLeft: 10,
  },
  footer: {
    alignItems: 'center',
    paddingVertical: 30,
  },
  footerText: {
    fontSize: 12,
    color: '#999',
  },
  footerVersion: {
    fontSize: 11,
    color: '#ccc',
    marginTop: 3,
  },
});
