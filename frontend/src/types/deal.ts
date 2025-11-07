import type { Product } from './product';

export interface Deal {
  id: number;
  product_id: number;
  product?: Product;
  original_price: number;
  deal_price: number;
  discount_percent: number;
  deal_type: 'price_drop' | 'coupon' | 'sale';
  description?: string;
  deal_start_date?: string;
  deal_end_date?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface DealFilter {
  status?: 'active' | 'expired';
  site?: string;
  discount_range_min?: number;
  discount_range_max?: number;
  deal_type?: string;
}