import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import * as SecureStore from 'expo-secure-store';

import { AuthResponse, UserProfile } from '../types/api';
import { setAuthToken } from '../api/client';

type AuthContextValue = {
  user: UserProfile | null;
  token: string | null;
  loading: boolean;
  login: (data: AuthResponse) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const TOKEN_KEY = 'traffic_token';
const USER_KEY = 'traffic_user';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const bootstrapAsync = useCallback(async () => {
    try {
      const storedToken = await SecureStore.getItemAsync(TOKEN_KEY);
      const storedUser = await SecureStore.getItemAsync(USER_KEY);
      if (storedToken && storedUser) {
        setToken(storedToken);
        setAuthToken(storedToken);
        setUser(JSON.parse(storedUser));
      }
    } catch (error) {
      console.warn('[Auth] bootstrap error', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    bootstrapAsync();
  }, [bootstrapAsync]);

  const login = useCallback(async (data: AuthResponse) => {
    const { token: accessToken, user: userProfile } = data;
    setToken(accessToken);
    setUser(userProfile);
    setAuthToken(accessToken);
    await SecureStore.setItemAsync(TOKEN_KEY, accessToken);
    await SecureStore.setItemAsync(USER_KEY, JSON.stringify(userProfile));
  }, []);

  const logout = useCallback(async () => {
    setToken(null);
    setUser(null);
    setAuthToken(undefined);
    await SecureStore.deleteItemAsync(TOKEN_KEY);
    await SecureStore.deleteItemAsync(USER_KEY);
  }, []);

  const value = useMemo(
    () => ({
      user,
      token,
      loading,
      login,
      logout,
    }),
    [user, token, loading, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

