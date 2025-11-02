import { useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API } from '../api/client';

interface User {
  telegram_id: number;
  username: string;
  first_name: string;
  balance_usd: number;
  is_active: boolean;
}

export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAuthData();
  }, []);

  const loadAuthData = async () => {
    try {
      const savedToken = await AsyncStorage.getItem('token');
      const savedUser = await AsyncStorage.getItem('user');

      if (savedToken && savedUser) {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
      }
    } catch (error) {
      console.error('Failed to load auth data:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (authData: any) => {
    try {
      const response = await API.auth.telegram(authData);
      
      if (response.access_token) {
        await AsyncStorage.setItem('token', response.access_token);
        await AsyncStorage.setItem('user', JSON.stringify(response.user));
        
        setToken(response.access_token);
        setUser(response.user);
        
        return { success: true };
      }
      
      return { success: false, error: 'No token received' };
    } catch (error: any) {
      console.error('Login error:', error);
      return { success: false, error: error.message };
    }
  };

  const logout = async () => {
    try {
      await AsyncStorage.removeItem('token');
      await AsyncStorage.removeItem('user');
      
      setToken(null);
      setUser(null);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const refreshUser = async () => {
    try {
      if (!token) return;
      
      const response = await API.profile.get();
      setUser(response);
      await AsyncStorage.setItem('user', JSON.stringify(response));
    } catch (error) {
      console.error('Failed to refresh user:', error);
    }
  };

  const updateBalance = (newBalance: number) => {
    if (user) {
      const updatedUser = { ...user, balance_usd: newBalance };
      setUser(updatedUser);
      AsyncStorage.setItem('user', JSON.stringify(updatedUser));
    }
  };

  return {
    user,
    token,
    loading,
    isAuthenticated: !!token && !!user,
    login,
    logout,
    refreshUser,
    updateBalance,
  };
};
