export interface UserProfile {
  id: number;
  telegram_id: number;
  username?: string;
  first_name?: string;
  photo_url?: string;
  auth_date?: string;
  balance_usd: number;
  sent_mb: number;
  used_mb: number;
  role?: string;
  notifications_enabled?: boolean;
}

export interface AuthResponse {
  status: string;
  user: UserProfile;
  token: string;
}

export interface DashboardBalance {
  usd: number;
  converted_usdt: number;
  converted_uzs: number;
  last_refreshed?: string;
}

export interface DashboardTraffic {
  sent_mb: number;
  used_mb: number;
  remaining_mb: number;
  current_speed?: number;
  session_id?: string;
  status?: string;
}

export interface DashboardPricing {
  date?: string;
  price_per_gb: number;
  message?: string;
  change?: number;
}

export interface DashboardStats {
  today_earn: number;
  week_earn: number;
  month_earn: number;
  average_speed?: number;
}

export interface DashboardResponse {
  user: UserProfile;
  balance: DashboardBalance;
  traffic: DashboardTraffic;
  pricing: DashboardPricing;
  mini_stats: DashboardStats;
}

export interface SessionItem {
  id: string;
  start_time: string;
  end_time?: string;
  duration?: string;
  sent_mb: number;
  earned_usd: number;
  status: string;
  ip_address?: string;
  location?: string;
  device?: string;
}

export interface SessionListResponse {
  items: SessionItem[];
  total: number;
}

export interface SessionSummary {
  today_sessions: number;
  today_mb: number;
  today_earnings: number;
  week_sessions: number;
  week_mb: number;
  week_earnings: number;
  average_per_session?: number;
}

export interface BalanceOverview {
  user: UserProfile;
  balance_usd: number;
  sent_mb: number;
  used_mb: number;
  today_earn: number;
  month_earn: number;
  transactions: Transaction[];
}

export interface Transaction {
  id: number;
  telegram_id: number;
  type: string;
  amount_usd: number;
  amount_usdt?: number;
  currency: string;
  status: string;
  wallet_address?: string;
  provider_payout_id?: string;
  tx_hash?: string;
  note?: string;
  created_at: string;
}

export interface TransactionsResponse {
  items: Transaction[];
  total: number;
}

export interface DailyPrice {
  date: string;
  price_per_gb: number;
  message?: string;
  change?: number;
}

export interface AnalyticsPoint {
  date: string;
  sent_mb: number;
  sold_mb: number;
  profit_usd: number;
  price_per_mb: number;
}

export interface AnalyticsResponse {
  period: string;
  points: AnalyticsPoint[];
}

export interface SupportRequest {
  id: number;
  telegram_id: number;
  subject: string;
  message: string;
  status: string;
  created_at: string;
  admin_reply?: string;
  reply_at?: string;
}

export interface SupportHistoryResponse {
  items: SupportRequest[];
}

export interface Announcement {
  id: number;
  title: string;
  description: string;
  image_url?: string;
  link?: string;
  created_at: string;
}

export interface PromoCode {
  id: number;
  code: string;
  bonus_percent: number;
  expires_at?: string;
  is_active: boolean;
  description?: string;
}

export interface NewsPromoResponse {
  telegram_links: Record<string, string>;
  announcements: Announcement[];
  promo: PromoCode[];
}

