import { useCallback, useState } from 'react';
import Toast from 'react-native-toast-message';

type AsyncFn<TArgs extends unknown[], TResponse> = (...args: TArgs) => Promise<TResponse>;

export const useApi = <TArgs extends unknown[], TResponse>(fn: AsyncFn<TArgs, TResponse>) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const wrapped = useCallback(
    async (...args: TArgs): Promise<TResponse | null> => {
      setLoading(true);
      setError(null);
      try {
        const response = await fn(...args);
        return response;
      } catch (err: any) {
        const message = err?.response?.data?.message || err?.message || 'Unknown error';
        setError(message);
        Toast.show({ type: 'error', text1: 'Xatolik', text2: message });
        return null;
      } finally {
        setLoading(false);
      }
    },
    [fn],
  );

  return { call: wrapped, loading, error };
};

