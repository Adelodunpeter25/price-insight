import { useState } from 'react';
import { Plus, Grid, List, Package } from 'lucide-react';
import { DashboardLayout } from '../components/layout/DashboardLayout';
import { ProductTable, ProductCard, ProductFilters, AddProductModal } from '../components/products';
import { Button } from '../components/common/Button';
import { Skeleton } from '../components/common/Skeleton';
import { ConfirmDialog } from '../components/common/ConfirmDialog';
import { useProducts } from '../hooks/useProducts';

const Products = () => {
  const { products, isLoading, removeProduct } = useProducts();
  const [viewMode, setViewMode] = useState<'table' | 'grid'>('table');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSite, setSelectedSite] = useState('');
  const [sortBy, setSortBy] = useState('name');
  const [showAddModal, setShowAddModal] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState<{ show: boolean; productId?: number; productName?: string }>({ show: false });

  const filteredProducts = products.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSite = !selectedSite || product.site === selectedSite;
    return matchesSearch && matchesSite;
  });

  const handleView = (id: number) => {
    // Navigate to product detail
    console.log('View product:', id);
  };

  const handleRemove = (id: number) => {
    const product = products.find(p => p.id === id);
    setConfirmDelete({ 
      show: true, 
      productId: id, 
      productName: product?.name 
    });
  };

  const confirmRemove = async () => {
    if (confirmDelete.productId) {
      await removeProduct(confirmDelete.productId);
      setConfirmDelete({ show: false });
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
            <Button variant="primary" onClick={() => setShowAddModal(true)}>
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
            <Button variant="primary" onClick={() => setShowAddModal(true)}>
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

        {/* Modals */}
        <AddProductModal
          isOpen={showAddModal}
          onClose={() => setShowAddModal(false)}
        />

        <ConfirmDialog
          isOpen={confirmDelete.show}
          onClose={() => setConfirmDelete({ show: false })}
          onConfirm={confirmRemove}
          title="Remove Product"
          message={`Are you sure you want to remove "${confirmDelete.productName}"? This action cannot be undone.`}
          confirmText="Remove"
          variant="danger"
        />
      </div>
    </DashboardLayout>
  );
};

export default Products;