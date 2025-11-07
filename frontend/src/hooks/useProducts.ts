import { useState, useEffect, useCallback } from 'react';
import type { Product, PriceHistory, CreateProductPayload, PaginatedResponse } from '../types';
import { apiClient } from '../services/api';

interface UseProductsReturn {
  products: Product[];
  isLoading: boolean;
  error: string | null;
  addProduct: (payload: CreateProductPayload) => Promise<Product>;
  removeProduct: (id: number) => Promise<void>;
  refreshProducts: () => Promise<void>;
  getProductDetail: (id: number) => Promise<Product>;
  getPriceHistory: (id: number) => Promise<PriceHistory[]>;
}

export const useProducts = (): UseProductsReturn => {
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshProducts = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await apiClient.get<PaginatedResponse<Product>>('/ecommerce/products');
      setProducts(response.data.items);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to fetch products');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const addProduct = useCallback(async (payload: CreateProductPayload): Promise<Product> => {
    try {
      const response = await apiClient.post<Product>('/ecommerce/products', payload);
      setProducts(prev => [response.data, ...prev]);
      return response.data;
    } catch (err: any) {
      const errorMsg = err.response?.data?.message || 'Failed to add product';
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, []);

  const removeProduct = useCallback(async (id: number): Promise<void> => {
    try {
      await apiClient.delete(`/ecommerce/products/${id}`);
      setProducts(prev => prev.filter(p => p.id !== id));
    } catch (err: any) {
      const errorMsg = err.response?.data?.message || 'Failed to remove product';
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, []);

  const getProductDetail = useCallback(async (id: number): Promise<Product> => {
    try {
      const response = await apiClient.get<Product>(`/ecommerce/products/${id}`);
      return response.data;
    } catch (err: any) {
      const errorMsg = err.response?.data?.message || 'Failed to fetch product';
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, []);

  const getPriceHistory = useCallback(async (id: number): Promise<PriceHistory[]> => {
    try {
      const response = await apiClient.get<PriceHistory[]>(`/ecommerce/products/${id}/price-history`);
      return response.data;
    } catch (err: any) {
      const errorMsg = err.response?.data?.message || 'Failed to fetch price history';
      setError(errorMsg);
      throw new Error(errorMsg);
    }
  }, []);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    refreshProducts();
    const interval = setInterval(refreshProducts, 30000);
    return () => clearInterval(interval);
  }, [refreshProducts]);

  return {
    products,
    isLoading,
    error,
    addProduct,
    removeProduct,
    refreshProducts,
    getProductDetail,
    getPriceHistory
  };
};