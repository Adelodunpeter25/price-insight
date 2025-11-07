import { useState, useEffect, useCallback, useMemo } from 'react';
import type { Alert, AlertFilter, PaginatedResponse } from '../types';
import { apiClient } from '../services/api';

interface UseAlertsReturn {
  alerts: Alert[];
  unreadCount: number;
  isLoading: boolean;
  error: string | null;
  refreshAlerts: () => Promise<void>;
  markAsRead: (id: number) => Promise<void>;
  dismissAlert: (id: number) => Promise<void>;
  markAllAsRead: () => Promise<void>;
}

export const useAlerts = (): UseAlertsReturn => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshAlerts = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await apiClient.get<PaginatedResponse<Alert>>('/alerts');
      setAlerts(response.data.items);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to fetch alerts');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const markAsRead = useCallback(async (id: number): Promise<void> => {
    try {
      await apiClient.post(`/alerts/${id}/mark-read`);
      setAlerts(prev => prev.map(alert => 
        alert.id === id ? { ...alert, is_read: true } : alert
      ));
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to mark alert as read');
      throw err;
    }
  }, []);

  const dismissAlert = useCallback(async (id: number): Promise<void> => {
    try {
      await apiClient.delete(`/alerts/${id}`);
      setAlerts(prev => prev.filter(alert => alert.id !== id));
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to dismiss alert');
      throw err;
    }
  }, []);

  const markAllAsRead = useCallback(async (): Promise<void> => {
    try {
      await apiClient.post('/alerts/mark-all-read');
      setAlerts(prev => prev.map(alert => ({ ...alert, is_read: true })));
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to mark all alerts as read');
      throw err;
    }
  }, []);

  const unreadCount = useMemo(() => {
    return alerts.filter(alert => !alert.is_read).length;
  }, [alerts]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    refreshAlerts();
    const interval = setInterval(refreshAlerts, 30000);
    return () => clearInterval(interval);
  }, [refreshAlerts]);

  return {
    alerts,
    unreadCount,
    isLoading,
    error,
    refreshAlerts,
    markAsRead,
    dismissAlert,
    markAllAsRead
  };
};