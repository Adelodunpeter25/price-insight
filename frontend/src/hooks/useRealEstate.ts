import { useState, useEffect } from 'react';

interface Property {
  id: number;
  title: string;
  location: string;
  current_price: number;
  is_tracked: boolean;
  created_at: string;
}

interface PropertyDeal {
  id: number;
  property_id: number;
  discount_percent: number;
  is_active: boolean;
  created_at: string;
}

interface PropertyAlert {
  id: number;
  property_id: number;
  message: string;
  created_at: string;
}

export const useRealEstate = () => {
  const [properties, setProperties] = useState<Property[]>([]);
  const [deals, setDeals] = useState<PropertyDeal[]>([]);
  const [alerts, setAlerts] = useState<PropertyAlert[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // TODO: Replace with actual API calls to:
    // GET /api/real-estate/properties
    // GET /api/real-estate/deals
    // GET /api/real-estate/alerts
    setProperties([]);
    setDeals([]);
    setAlerts([]);
    setIsLoading(false);
  }, []);

  return {
    properties,
    deals,
    alerts,
    isLoading,
    totalItems: properties.length,
    activeDeals: deals.filter(d => d.is_active).length
  };
};