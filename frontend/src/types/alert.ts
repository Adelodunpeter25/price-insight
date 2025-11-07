import type { Product } from './product';

export interface AlertRule {
  id: number;
  product_id: number;
  product?: Product;
  rule_type: 'price_drop' | 'threshold' | 'deal_appeared';
  threshold_value?: number;
  percentage_threshold?: number;
  notification_method: 'console' | 'email' | 'file';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AlertHistory {
  id: number;
  alert_rule_id: number;
  product_id: number;
  alert_rule?: AlertRule;
  product?: Product;
  trigger_value: number;
  message: string;
  notification_sent: boolean;
  created_at: string;
  updated_at: string;
}

export interface Alert extends AlertHistory {
  alert_type: AlertRule['rule_type'];
  old_value?: number;
  new_value: number;
  is_read: boolean;
}

export interface AlertFilter {
  types?: AlertRule['rule_type'][];
  product_id?: number;
  date_from?: string;
  date_to?: string;
  is_read?: boolean;
}