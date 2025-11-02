import axios from 'axios';
import Constants from 'expo-constants';

const extra = Constants?.expoConfig?.extra || Constants?.manifest?.extra || {};

export const API_BASE_URL = extra?.apiUrl || 'https://113.30.191.89/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

export const setAuthToken = (token?: string): void => {
  if (token) {
    apiClient.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete apiClient.defaults.headers.common.Authorization;
  }
};

apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      console.error('[API error]', error.response.status, error.response.data);
    } else {
      console.error('[API error]', error.message);
    }
    return Promise.reject(error);
  },
);

