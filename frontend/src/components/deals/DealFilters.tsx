import { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { Button } from '../common/Button';
import type { DealFilter } from '../../types';

interface DealFiltersProps {
  filters: DealFilter;
  onFiltersChange: (filters: DealFilter) => void;
}

export const DealFilters = ({ filters, onFiltersChange }: DealFiltersProps) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleStatusChange = (status: string, checked: boolean) => {
    onFiltersChange({
      ...filters,
      status: checked ? (status as 'active' | 'expired') : undefined
    });
  };

  const handleDiscountRangeChange = (min?: number, max?: number) => {
    onFiltersChange({
      ...filters,
      discount_range_min: min,
      discount_range_max: max
    });
  };

  return (
    <div className="glass-card rounded-lg p-4 mb-6">
      <div className="flex items-center justify-between mb-4 lg:mb-0">
        <h3 className="text-white font-medium">Filters</h3>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsExpanded(!isExpanded)}
          className="lg:hidden"
        >
          {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </Button>
      </div>

      <div className={`${isExpanded ? 'block' : 'hidden'} lg:block`}>
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
          {/* Status Filter */}
          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-2">Status</label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={filters.status === 'active'}
                  onChange={(e) => handleStatusChange('active', e.target.checked)}
                  className="mr-2 rounded"
                />
                <span className="text-sm text-zinc-300">Active</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={filters.status === 'expired'}
                  onChange={(e) => handleStatusChange('expired', e.target.checked)}
                  className="mr-2 rounded"
                />
                <span className="text-sm text-zinc-300">Expired</span>
              </label>
            </div>
          </div>

          {/* Site Filter */}
          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-2">Site</label>
            <select
              value={filters.site || ''}
              onChange={(e) => onFiltersChange({ ...filters, site: e.target.value || undefined })}
              className="w-full px-3 py-2 bg-zinc-900/50 border border-zinc-700/50 rounded-lg text-white text-sm"
            >
              <option value="">All Sites</option>
              <option value="amazon">Amazon</option>
              <option value="jumia">Jumia</option>
              <option value="konga">Konga</option>
            </select>
          </div>

          {/* Discount Range */}
          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-2">Min Discount %</label>
            <input
              type="number"
              min="0"
              max="100"
              value={filters.discount_range_min || ''}
              onChange={(e) => handleDiscountRangeChange(
                e.target.value ? Number(e.target.value) : undefined,
                filters.discount_range_max
              )}
              className="w-full px-3 py-2 bg-zinc-900/50 border border-zinc-700/50 rounded-lg text-white text-sm"
              placeholder="0"
            />
          </div>

          {/* Sort */}
          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-2">Sort By</label>
            <select className="w-full px-3 py-2 bg-zinc-900/50 border border-zinc-700/50 rounded-lg text-white text-sm">
              <option value="discount">Discount %</option>
              <option value="expiry">Expiry Date</option>
              <option value="price">Price</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
};