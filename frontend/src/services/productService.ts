import type { Product, PriceHistory, CreateProductPayload, PaginatedResponse } from '../types';
import { apiClient } from './api';

export const productService = {
  async getProducts(page = 1, limit = 20): Promise<PaginatedResponse<Product>> {
    const response = await apiClient.get<PaginatedResponse<Product>>('/ecommerce/products', {
      params: { page, limit }
    });
    return response.data;
  },

  async getProduct(id: number): Promise<Product> {
    const response = await apiClient.get<Product>(`/ecommerce/products/${id}`);
    return response.data;
  },

  async addProduct(payload: CreateProductPayload): Promise<Product> {
    const response = await apiClient.post<Product>('/ecommerce/products', payload);
    return response.data;
  },

  async removeProduct(id: number): Promise<void> {
    await apiClient.delete(`/ecommerce/products/${id}`);
  },

  async getPriceHistory(id: number): Promise<PriceHistory[]> {
    const response = await apiClient.get<PriceHistory[]>(`/ecommerce/products/${id}/price-history`);
    return response.data;
  },

  async searchProducts(query: string): Promise<Product[]> {
    const response = await apiClient.get<Product[]>('/ecommerce/products/search', {
      params: { q: query }
    });
    return response.data;
  }
};