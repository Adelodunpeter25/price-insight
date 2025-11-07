import { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { Button } from '../common/Button';
import type { AlertFilter } from '../../types';

interface AlertFiltersProps {
  filters: AlertFilter;
  onFiltersChange: (filters: AlertFilter) => void;
}

export const AlertFilters = ({ filters, onFiltersChange }: AlertFiltersProps) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleTypeChange = (type: string, checked: boolean) => {
    const currentTypes = filters.types || [];
    const newTypes = checked
      ? [...currentTypes, type as any]
      : currentTypes.filter(t => t !== type);
    
    onFiltersChange({
      ...filters,
      types: newTypes.length > 0 ? newTypes : undefined
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
          {/* Alert Types */}
          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-2">Alert Types</label>
            <div className="space-y-2">
              {['price_drop', 'threshold', 'deal_appeared'].map(type => (
                <label key={type} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={filters.types?.includes(type as any) || false}
                    onChange={(e) => handleTypeChange(type, e.target.checked)}
                    className="mr-2 rounded"
                  />
                  <span className="text-sm text-zinc-300 capitalize">
                    {type.replace('_', ' ')}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Read Status */}
          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-2">Status</label>
            <select
              value={filters.is_read === undefined ? '' : filters.is_read.toString()}
              onChange={(e) => onFiltersChange({
                ...filters,
                is_read: e.target.value === '' ? undefined : e.target.value === 'true'
              })}
              className="w-full px-3 py-2 bg-zinc-900/50 border border-zinc-700/50 rounded-lg text-white text-sm"
            >
              <option value="">All</option>
              <option value="false">Unread</option>
              <option value="true">Read</option>
            </select>
          </div>

          {/* Date From */}
          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-2">From Date</label>
            <input
              type="date"
              value={filters.date_from || ''}
              onChange={(e) => onFiltersChange({
                ...filters,
                date_from: e.target.value || undefined
              })}
              className="w-full px-3 py-2 bg-zinc-900/50 border border-zinc-700/50 rounded-lg text-white text-sm"
            />
          </div>

          {/* Date To */}
          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-2">To Date</label>
            <input
              type="date"
              value={filters.date_to || ''}
              onChange={(e) => onFiltersChange({
                ...filters,
                date_to: e.target.value || undefined
              })}
              className="w-full px-3 py-2 bg-zinc-900/50 border border-zinc-700/50 rounded-lg text-white text-sm"
            />
          </div>
        </div>
      </div>
    </div>
  );
};