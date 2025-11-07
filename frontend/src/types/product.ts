export interface Product {
  id: number;
  name: string;
  url: string;
  site: string;
  category?: string;
  is_tracked: boolean;
  created_at: string;
  updated_at: string;
}

export interface PriceHistory {
  id: number;
  product_id: number;
  price: number;
  currency: string;
  created_at: string;
}

export interface CreateProductPayload {
  name: string;
  url: string;
  category?: string;
}

export interface ProductStats {
  total_count: number;
  active_deals_count: number;
  price_drops_week: number;
}