export const formatCurrency = (value: number, currency: 'USD' | 'UZS' | 'USDT' = 'USD'): string => {
  try {
    return Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
      minimumFractionDigits: currency === 'UZS' ? 0 : 2,
    }).format(value);
  } catch (error) {
    const symbol = currency === 'USD' ? '$' : currency === 'USDT' ? '?' : 'so?m';
    return `${symbol}${value.toFixed(currency === 'UZS' ? 0 : 2)}`;
  }
};

export const formatMb = (value: number): string => {
  if (value >= 1024) {
    return `${(value / 1024).toFixed(2)} GB`;
  }
  return `${value.toFixed(1)} MB`;
};

export const formatSpeed = (value?: number): string => {
  if (!value) return '?';
  if (value >= 1) return `${value.toFixed(2)} MB/s`;
  return `${(value * 1024).toFixed(0)} KB/s`;
};

export const utcToLocal = (iso?: string): string => {
  if (!iso) return '?';
  const date = new Date(iso);
  return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
};

