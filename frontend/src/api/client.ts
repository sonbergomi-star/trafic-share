import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// API Base URL - VPS IP
const API_BASE_URL = 'http://113.30.191.89/api';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('jwt_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      await AsyncStorage.removeItem('jwt_token');
      await AsyncStorage.removeItem('user_data');
      // Navigate to login screen
    }
    return Promise.reject(error);
  }
);

export default apiClient;

// API endpoints
export const API = {
  // Auth
  telegramAuth: (data: any) => apiClient.post('/auth/telegram', data),
  logout: (telegramId: number) => apiClient.post('/auth/logout', { telegram_id: telegramId }),

  // Dashboard
  getDashboard: (telegramId: number) => apiClient.get(`/dashboard/${telegramId}`),

  // Balance
  getBalance: (telegramId: number) => apiClient.get(`/balance/${telegramId}`),
  refreshBalance: (telegramId: number) => apiClient.post('/balance/refresh', { telegram_id: telegramId }),

  // Withdraw
  createWithdraw: (data: any) => apiClient.post('/withdraw', data),
  getWithdrawHistory: (telegramId: number) => apiClient.get(`/withdraw/history/${telegramId}`),

  // Statistics
  getDailyStats: (telegramId: number) => apiClient.get(`/stats/daily/${telegramId}`),
  getWeeklyStats: (telegramId: number) => apiClient.get(`/stats/weekly/${telegramId}`),
  getMonthlyStats: (telegramId: number) => apiClient.get(`/stats/monthly/${telegramId}`),

  // Sessions
  startSession: (data: any) => apiClient.post('/sessions/start', data),
  stopSession: (sessionId: string) => apiClient.post(`/sessions/stop?session_id=${sessionId}`),
  getSessions: (telegramId: number) => apiClient.get(`/sessions/${telegramId}`),

  // Support
  createSupportRequest: (data: any) => apiClient.post('/support/send', data),
  getSupportHistory: (telegramId: number) => apiClient.get(`/support/history/${telegramId}`),

  // News
  getAnnouncements: () => apiClient.get('/news/announcements'),
  getPromoCodes: () => apiClient.get('/news/promo'),
  getTelegramLinks: () => apiClient.get('/news/telegram_links'),

  // Profile
  getProfile: (telegramId: number) => apiClient.get(`/profile/${telegramId}`),
  renewToken: (telegramId: number) => apiClient.post('/profile/token/renew', { telegram_id: telegramId }),
  getSettings: (telegramId: number) => apiClient.get(`/profile/settings/${telegramId}`),
  updateSettings: (telegramId: number, data: any) => apiClient.patch(`/profile/settings/${telegramId}`, data),
};
