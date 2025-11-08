import { useState, useEffect } from 'react';

interface UtilityService {
  id: number;
  name: string;
  provider: string;
  service_type: string;
  current_price: number;
  is_tracked: boolean;
  created_at: string;
}

interface UtilityDeal {
  id: number;
  service_id: number;
  discount_percent: number;
  is_active: boolean;
  created_at: string;
}

interface UtilityAlert {
  id: number;
  service_id: number;
  message: string;
  created_at: string;
}

export const useUtilities = () => {
  const [services, setServices] = useState<UtilityService[]>([]);
  const [deals, setDeals] = useState<UtilityDeal[]>([]);
  const [alerts, setAlerts] = useState<UtilityAlert[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // TODO: Replace with actual API calls to:
    // GET /api/utilities/services
    // GET /api/utilities/deals  
    // GET /api/utilities/alerts
    setServices([]);
    setDeals([]);
    setAlerts([]);
    setIsLoading(false);
  }, []);

  return {
    services,
    deals,
    alerts,
    isLoading,
    totalItems: services.length,
    activeDeals: deals.filter(d => d.is_active).length
  };
};