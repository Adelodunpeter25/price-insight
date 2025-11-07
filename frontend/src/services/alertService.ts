import type { Alert, AlertFilter, PaginatedResponse } from '../types';
import { apiClient } from './api';

export const alertService = {
  async getAlerts(filters?: AlertFilter): Promise<PaginatedResponse<Alert>> {
    const params = new URLSearchParams();
    
    if (filters?.types?.length) {
      filters.types.forEach(type => params.append('types', type));
    }
    if (filters?.product_id) params.append('product_id', filters.product_id.toString());
    if (filters?.date_from) params.append('date_from', filters.date_from);
    if (filters?.date_to) params.append('date_to', filters.date_to);
    if (filters?.is_read !== undefined) params.append('is_read', filters.is_read.toString());

    const response = await apiClient.get<PaginatedResponse<Alert>>(`/alerts?${params}`);
    return response.data;
  },

  async markAsRead(id: number): Promise<void> {
    await apiClient.post(`/alerts/${id}/mark-read`);
  },

  async dismissAlert(id: number): Promise<void> {
    await apiClient.delete(`/alerts/${id}`);
  },

  async markAllAsRead(): Promise<void> {
    await apiClient.post('/alerts/mark-all-read');
  },

  async getUnreadCount(): Promise<number> {
    const response = await apiClient.get<{ count: number }>('/alerts/unread-count');
    return response.data.count;
  }
};