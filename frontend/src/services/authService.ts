import type { LoginPayload, SignupPayload, AuthResponse, User } from '../types';
import { apiClient } from './api';

export const authService = {
  async login(payload: LoginPayload): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/login', payload);
    return response.data;
  },

  async signup(payload: SignupPayload): Promise<AuthResponse> {
    await apiClient.post('/auth/register', payload);
    return this.login({ email: payload.email, password: payload.password });
  },

  async logout(): Promise<void> {
    // Clear tokens locally (backend doesn't need logout endpoint)
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },

  async refreshToken(refreshToken: string): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/refresh', {
      refresh_token: refreshToken
    });
    return response.data;
  }
};