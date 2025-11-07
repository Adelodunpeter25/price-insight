import { useState, useCallback, useEffect } from 'react';
import type { User, LoginPayload, SignupPayload } from '../types';
import { authService } from '../services/authService';

interface UseAuthReturn {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  login: (payload: LoginPayload) => Promise<void>;
  signup: (payload: SignupPayload) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  refreshToken: () => Promise<boolean>;
}

export const useAuth = (): UseAuthReturn => {
  const [user, setUser] = useState<User | null>(null);
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
      setUser(null);
      return false;
    }
  }, []);

  const login = useCallback(async (payload: LoginPayload) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await authService.login(payload);
      
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      
      const user = await authService.getCurrentUser();
      setUser(user);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const signup = useCallback(async (payload: SignupPayload) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await authService.signup(payload);
      
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      
      const user = await authService.getCurrentUser();
      setUser(user);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Signup failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    await authService.logout();
    setUser(null);
  }, []);

  // Auto-login on mount
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        const user = await authService.getCurrentUser();
        setUser(user);
      } catch {
        // Try refresh token
        const refreshed = await refreshToken();
        if (refreshed) {
          try {
            const user = await authService.getCurrentUser();
            setUser(user);
          } catch {
            await logout();
          }
        }
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, [refreshToken, logout]);

  return {
    user,
    isLoading,
    error,
    login,
    signup,
    logout,
    isAuthenticated: !!user,
    refreshToken
  };
};