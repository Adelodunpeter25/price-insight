import { useState, useEffect, useCallback, useRef } from 'react';
import { apiClient } from '../services/api';

interface UseFetchReturn<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  mutate: (newData: T) => void;
}

export const useFetch = <T>(url: string, options?: { enabled?: boolean }): UseFetchReturn<T> => {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const retryCountRef = useRef(0);

  const fetchData = useCallback(async () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();
    setIsLoading(true);
    setError(null);

    const maxRetries = 3;
    const baseDelay = 1000;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const response = await apiClient.get<T>(url, {
          signal: abortControllerRef.current.signal
        });
        
        setData(response.data);
        retryCountRef.current = 0;
        break;
      } catch (err: any) {
        if (err.name === 'AbortError') break;
        
        if (attempt === maxRetries) {
          setError(err.response?.data?.message || 'Failed to fetch data');
          retryCountRef.current = 0;
        } else {
          // Exponential backoff
          await new Promise(resolve => 
            setTimeout(resolve, baseDelay * Math.pow(2, attempt))
          );
        }
      }
    }
    
    setIsLoading(false);
  }, [url]);

  const refetch = useCallback(async () => {
    await fetchData();
  }, [fetchData]);

  const mutate = useCallback((newData: T) => {
    setData(newData);
  }, []);

  useEffect(() => {
    if (options?.enabled !== false) {
      fetchData();
    }

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [fetchData, options?.enabled]);

  // Clear error after 5 seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  return { data, isLoading, error, refetch, mutate };
};