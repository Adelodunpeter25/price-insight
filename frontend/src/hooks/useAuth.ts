import { useState, useCallback, useEffect } from 'react';
import type { User, LoginPayload, SignupPayload } from '../types';
import { authService } from '../services/authService';
import { useAuthStore } from '../store/authStore';

interface UseAuthReturn {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  login: (payload: LoginPayload) => Promise<void>;
  signup: (payload: SignupPayload) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
  refreshToken: () => Promise<boolean>;
}

export const useAuth = (): UseAuthReturn => {
  const { user, isAuthenticated, setUser, clearAuth } = useAuthStore();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refreshToken = useCallback(async (): Promise<boolean> => {
    try {
      const refreshTokenValue = localStorage.getItem('refresh_token');
      if (!refreshTokenValue) return false;

      const response = await authService.refreshToken(refreshTokenValue);
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      return true;
    } catch {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      clearAuth();
      return false;
    }
  }, [clearAuth]);

  const login = useCallback(async (payload: LoginPayload) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await authService.login(payload);
      
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      
      const userData = await authService.getCurrentUser();
      setUser(userData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [setUser]);

  const signup = useCallback(async (payload: SignupPayload) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await authService.signup(payload);
      
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      
      const userData = await authService.getCurrentUser();
      setUser(userData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Signup failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [setUser]);

  const logout = useCallback(async () => {
    await authService.logout();
    clearAuth();
  }, [clearAuth]);

  // Auto-login on mount
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        const userData = await authService.getCurrentUser();
        setUser(userData);
      } catch {
        // Try refresh token
        const refreshed = await refreshToken();
        if (refreshed) {
          try {
            const userData = await authService.getCurrentUser();
            setUser(userData);
          } catch {
            // Don't call logout here as it might cause redirect
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            clearAuth();
          }
        } else {
          // Clear auth silently without logout
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          clearAuth();
        }
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, [refreshToken, setUser, clearAuth]);

  return {
    user,
    isLoading,
    error,
    login,
    signup,
    logout,
    isAuthenticated,
    refreshToken
  };
};