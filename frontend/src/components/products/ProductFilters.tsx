import { Search, Filter } from 'lucide-react';
import { Input } from '../common/Input';
import { Button } from '../common/Button';

interface ProductFiltersProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  selectedSite: string;
  onSiteChange: (site: string) => void;
  sortBy: string;
  onSortChange: (sort: string) => void;
}

export const ProductFilters = ({
  searchQuery,
  onSearchChange,
  selectedSite,
  onSiteChange,
  sortBy,
  onSortChange
}: ProductFiltersProps) => {
  return (
    <div className="glass-card rounded-lg p-4 mb-6">
      <div className="flex flex-col lg:flex-row gap-4">
        <div className="flex-1">
          <Input
            placeholder="Search products..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            leftIcon={<Search size={16} />}
          />
        </div>
        
        <div className="flex gap-2">
          <select
            value={selectedSite}
            onChange={(e) => onSiteChange(e.target.value)}
            className="px-3 py-2 bg-zinc-900/50 border border-zinc-700/50 rounded-lg text-white text-sm"
          >
            <option value="">All Sites</option>
            <option value="amazon">Amazon</option>
            <option value="jumia">Jumia</option>
            <option value="konga">Konga</option>
          </select>
          
          <select
            value={sortBy}
            onChange={(e) => onSortChange(e.target.value)}
            className="px-3 py-2 bg-zinc-900/50 border border-zinc-700/50 rounded-lg text-white text-sm"
          >
            <option value="name">Name</option>
            <option value="price">Price</option>
            <option value="date">Date Added</option>
          </select>
        </div>
      </div>
    </div>
  );
};