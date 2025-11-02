import { apiClient } from './client';
import {
  AnalyticsResponse,
  AuthResponse,
  BalanceOverview,
  DashboardResponse,
  NewsPromoResponse,
  SessionListResponse,
  SessionSummary,
  SupportHistoryResponse,
  TransactionsResponse,
  UserProfile,
} from '../types/api';

export const AuthApi = {
  telegramLogin: (payload: Record<string, unknown>) => apiClient.post<AuthResponse>('/auth/telegram', payload),
};

export const DashboardApi = {
  getDashboard: (telegramId: number) => apiClient.get<DashboardResponse>(`/dashboard/${telegramId}`),
};

export const TrafficApi = {
  start: (payload: Record<string, unknown>) => apiClient.post('/traffic/start', payload),
  stop: (sessionId: string) => apiClient.post('/traffic/stop', { session_id: sessionId }),
};

export const SessionApi = {
  list: (params?: { limit?: number; offset?: number }) =>
    apiClient.get<SessionListResponse>('/sessions', { params }),
  summary: () => apiClient.get<SessionSummary>('/sessions/summary'),
};

export const BalanceApi = {
  overview: (telegramId: number) => apiClient.get<BalanceOverview>(`/user/balance/${telegramId}`),
  transactions: (params?: { limit?: number; offset?: number }) =>
    apiClient.get<TransactionsResponse>('/transactions', { params }),
  refresh: (payload: { telegram_id: number; delta?: number }) =>
    apiClient.post('/user/refresh_balance', payload),
  withdraw: (payload: { telegram_id: number; amount_usd: number; wallet_address: string; network?: string }) =>
    apiClient.post('/withdraw', payload),
};

export const AnalyticsApi = {
  daily: (telegramId: number) => apiClient.get<AnalyticsResponse>(`/stats/daily/${telegramId}`),
  weekly: (telegramId: number) => apiClient.get<AnalyticsResponse>(`/stats/weekly/${telegramId}`),
  monthly: (telegramId: number) => apiClient.get<AnalyticsResponse>(`/stats/monthly/${telegramId}`),
};

export const SupportApi = {
  history: () => apiClient.get<SupportHistoryResponse>('/support/history'),
  send: (payload: { telegram_id: number; subject: string; message: string; attachment_url?: string }) =>
    apiClient.post('/support/send', payload),
};

export const NewsApi = {
  list: () => apiClient.get<NewsPromoResponse>('/news_promo'),
  activatePromo: (payload: { user_id: number; code: string }) => apiClient.post('/promo/activate', payload),
};

export const UserApi = {
  profile: () => apiClient.get<UserProfile>('/user/profile'),
  renewToken: () => apiClient.post('/user/token/renew'),
  updateSettings: (payload: Record<string, unknown>) => apiClient.patch('/user/settings', payload),
  logout: () => apiClient.post('/user/logout'),
  logoutAll: () => apiClient.post('/user/logout_all'),
};

