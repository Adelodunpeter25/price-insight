import { useState } from 'react';
import { Plus, Grid, List } from 'lucide-react';
import { DashboardLayout } from '../components/layout/DashboardLayout';
import { ProductTable, ProductCard, ProductFilters } from '../components/products';
import { Button } from '../components/common/Button';
import { Skeleton } from '../components/common/Skeleton';
import { useProducts } from '../hooks/useProducts';

export const Products = () => {
  const { products, isLoading, removeProduct } = useProducts();
  const [viewMode, setViewMode] = useState<'table' | 'grid'>('table');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSite, setSelectedSite] = useState('');
  const [sortBy, setSortBy] = useState('name');

  const filteredProducts = products.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSite = !selectedSite || product.site === selectedSite;
    return matchesSearch && matchesSite;
  });

  const handleView = (id: number) => {
    // Navigate to product detail
    console.log('View product:', id);
  };

  const handleRemove = async (id: number) => {
    if (confirm('Are you sure you want to remove this product?')) {
      await removeProduct(id);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Products</h1>
            <p className="text-zinc-400 mt-1">Manage your tracked products</p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="flex bg-zinc-800 rounded-lg p-1">
              <Button
                variant={viewMode === 'table' ? 'primary' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('table')}
              >
                <List size={16} />
              </Button>
              <Button
                variant={viewMode === 'grid' ? 'primary' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('grid')}
              >
                <Grid size={16} />
              </Button>
            </div>
            <Button variant="primary">
              <Plus size={16} className="mr-2" />
              Add Product
            </Button>
          </div>
        </div>

        {/* Filters */}
        <ProductFilters
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          selectedSite={selectedSite}
          onSiteChange={setSelectedSite}
          sortBy={sortBy}
          onSortChange={setSortBy}
        />

        {/* Content */}
        {isLoading ? (
          <div className="space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} variant="card" />
            ))}
          </div>
        ) : filteredProducts.length === 0 ? (
          <div className="text-center py-12">
            <Package className="w-12 h-12 text-zinc-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-white mb-2">No products found</h3>
            <p className="text-zinc-400 mb-4">
              {searchQuery || selectedSite ? 'Try adjusting your filters' : 'Start by adding your first product'}
            </p>
            <Button variant="primary">
              <Plus size={16} className="mr-2" />
              Add Product
            </Button>
          </div>
        ) : viewMode === 'table' ? (
          <div className="glass-card rounded-lg overflow-hidden">
            <ProductTable
              products={filteredProducts}
              onView={handleView}
              onRemove={handleRemove}
            />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredProducts.map(product => (
              <ProductCard
                key={product.id}
                product={product}
                onView={handleView}
                onRemove={handleRemove}
              />
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};