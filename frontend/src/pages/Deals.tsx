import { useState } from 'react';
import { Tag } from 'lucide-react';
import { DashboardLayout } from '../components/layout/DashboardLayout';
import { DealGrid, DealFilters } from '../components/deals';
import { Skeleton } from '../components/common/Skeleton';
import { Button } from '../components/common/Button';
import { useDeals } from '../hooks/useDeals';
import type { DealFilter } from '../types';

const Deals = () => {
  const { deals, isLoading, filteredDeals, setFilter } = useDeals();
  const [filters, setFilters] = useState<DealFilter>({});

  const handleFiltersChange = (newFilters: DealFilter) => {
    setFilters(newFilters);
    setFilter(newFilters);
  };

  const handleView = (productId: number) => {
    // Navigate to product detail or external URL
    console.log('View deal for product:', productId);
  };

  const handleAddAlert = (productId: number) => {
    // Open add alert modal
    console.log('Add alert for product:', productId);
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Deals</h1>
            <p className="text-zinc-400 mt-1">Discover the best deals and discounts</p>
          </div>
          <div className="text-sm text-zinc-400">
            {filteredDeals.length} deals found
          </div>
        </div>

        {/* Filters */}
        <DealFilters
          filters={filters}
          onFiltersChange={handleFiltersChange}
        />

        {/* Content */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <Skeleton key={i} variant="card" />
            ))}
          </div>
        ) : filteredDeals.length === 0 ? (
          <div className="text-center py-12">
            <Tag className="w-12 h-12 text-zinc-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-white mb-2">No deals found</h3>
            <p className="text-zinc-400 mb-4">
              {Object.keys(filters).length > 0 
                ? 'Try adjusting your filters to see more deals' 
                : 'Check back later for new deals and discounts'
              }
            </p>
            <Button 
              variant="ghost" 
              onClick={() => handleFiltersChange({})}
            >
              Clear Filters
            </Button>
          </div>
        ) : (
          <DealGrid
            deals={filteredDeals}
            onView={handleView}
            onAddAlert={handleAddAlert}
          />
        )}
      </div>
    </DashboardLayout>
  );
};

export default Deals;