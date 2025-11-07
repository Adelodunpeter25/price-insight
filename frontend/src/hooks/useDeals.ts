import { useState, useEffect, useCallback, useMemo } from 'react';
import type { Deal, DealFilter } from '../types';
import { dealService } from '../services/dealService';

interface UseDealsReturn {
  deals: Deal[];
  isLoading: boolean;
  error: string | null;
  refreshDeals: () => Promise<void>;
  filteredDeals: Deal[];
  setFilter: (filter: DealFilter) => void;
}

export const useDeals = (): UseDealsReturn => {
  const [deals, setDeals] = useState<Deal[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<DealFilter>({});

  const refreshDeals = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await dealService.getDeals(filter);
      setDeals(response.items);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to fetch deals');
    } finally {
      setIsLoading(false);
    }
  }, [filter]);

  const filteredDeals = useMemo(() => {
    let filtered = [...deals];

    if (filter.discount_range_min !== undefined) {
      filtered = filtered.filter(deal => deal.discount_percent >= filter.discount_range_min!);
    }

    if (filter.discount_range_max !== undefined) {
      filtered = filtered.filter(deal => deal.discount_percent <= filter.discount_range_max!);
    }

    // Sort by discount percentage (highest first)
    filtered.sort((a, b) => b.discount_percent - a.discount_percent);

    return filtered;
  }, [deals, filter]);

  // Auto-refresh every 60 seconds
  useEffect(() => {
    refreshDeals();
    const interval = setInterval(refreshDeals, 60000);
    return () => clearInterval(interval);
  }, [refreshDeals]);

  return {
    deals,
    isLoading,
    error,
    refreshDeals,
    filteredDeals,
    setFilter
  };
};