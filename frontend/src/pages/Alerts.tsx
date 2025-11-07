import { useState } from 'react';
import { Bell } from 'lucide-react';
import { DashboardLayout } from '../components/layout/DashboardLayout';
import { AlertList, AlertFilters } from '../components/alerts';
import { Skeleton } from '../components/common/Skeleton';
import { Button } from '../components/common/Button';
import { useAlerts } from '../hooks/useAlerts';
import type { AlertFilter } from '../types';

export const Alerts = () => {
  const { 
    alerts, 
    isLoading, 
    unreadCount, 
    markAsRead, 
    dismissAlert, 
    markAllAsRead 
  } = useAlerts();
  const [filters, setFilters] = useState<AlertFilter>({});

  const filteredAlerts = alerts.filter(alert => {
    if (filters.types?.length && !filters.types.includes(alert.alert_type)) return false;
    if (filters.is_read !== undefined && alert.is_read !== filters.is_read) return false;
    if (filters.product_id && alert.product_id !== filters.product_id) return false;
    
    if (filters.date_from) {
      const alertDate = new Date(alert.created_at);
      const fromDate = new Date(filters.date_from);
      if (alertDate < fromDate) return false;
    }
    
    if (filters.date_to) {
      const alertDate = new Date(alert.created_at);
      const toDate = new Date(filters.date_to);
      if (alertDate > toDate) return false;
    }
    
    return true;
  });

  const handleViewProduct = (productId: number) => {
    // Navigate to product detail
    console.log('View product:', productId);
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Alerts</h1>
            <p className="text-zinc-400 mt-1">
              Stay updated with price changes and deals
              {unreadCount > 0 && (
                <span className="ml-2 text-accent">({unreadCount} unread)</span>
              )}
            </p>
          </div>
        </div>

        {/* Filters */}
        <AlertFilters
          filters={filters}
          onFiltersChange={setFilters}
        />

        {/* Content */}
        {isLoading ? (
          <div className="space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} variant="card" />
            ))}
          </div>
        ) : filteredAlerts.length === 0 ? (
          <div className="text-center py-12">
            <Bell className="w-12 h-12 text-zinc-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-white mb-2">No alerts found</h3>
            <p className="text-zinc-400 mb-4">
              {Object.keys(filters).length > 0 
                ? 'Try adjusting your filters to see more alerts' 
                : 'You\'ll see price alerts and notifications here'
              }
            </p>
            <Button 
              variant="ghost" 
              onClick={() => setFilters({})}
            >
              Clear Filters
            </Button>
          </div>
        ) : (
          <AlertList
            alerts={filteredAlerts}
            onMarkAsRead={markAsRead}
            onDismiss={dismissAlert}
            onViewProduct={handleViewProduct}
            onMarkAllAsRead={markAllAsRead}
            hasUnread={unreadCount > 0}
          />
        )}
      </div>
    </DashboardLayout>
  );
};