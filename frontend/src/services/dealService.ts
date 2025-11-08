import type { Deal, DealFilter, PaginatedResponse } from '../types';
import { apiClient } from './api';

export const dealService = {
  async getDeals(filters?: DealFilter): Promise<PaginatedResponse<Deal>> {
    const params = new URLSearchParams();
    
    if (filters?.status) params.append('status', filters.status);
    if (filters?.site) params.append('site', filters.site);
    if (filters?.deal_type) params.append('deal_type', filters.deal_type);
    if (filters?.discount_range_min) params.append('discount_min', filters.discount_range_min.toString());
    if (filters?.discount_range_max) params.append('discount_max', filters.discount_range_max.toString());

    const response = await apiClient.get<PaginatedResponse<Deal>>(`/e-commerce/deals?${params}`);
    return response.data;
  },

  async getDeal(id: number): Promise<Deal> {
    const response = await apiClient.get<Deal>(`/e-commerce/deals/${id}/`);
    return response.data;
  }
};