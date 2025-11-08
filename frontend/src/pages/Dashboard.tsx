import { useState } from 'react';
import { motion } from 'framer-motion';
import { Package, Tag, Bell, TrendingDown, Plus, Plane, Home, Zap } from 'lucide-react';
import { DashboardLayout } from '../components/layout/DashboardLayout';
import { StatCard } from '../components/dashboard/StatCard';
import { AddProductModal } from '../components/products/AddProductModal';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import { useProducts } from '../hooks/useProducts';
import { useDeals } from '../hooks/useDeals';
import { useAlerts } from '../hooks/useAlerts';
import { useTravel } from '../hooks/useTravel';
import { useRealEstate } from '../hooks/useRealEstate';
import { useUtilities } from '../hooks/useUtilities';

const Dashboard = () => {
  const { products } = useProducts();
  const { deals } = useDeals();
  const { alerts, unreadCount } = useAlerts();
  const { flights, hotels } = useTravel();
  const { properties, activeDeals: realEstateDeals } = useRealEstate();
  const { services, activeDeals: utilityDeals } = useUtilities();
  const [showAddModal, setShowAddModal] = useState(false);

  // Calculate totals across all categories
  const totalItems = products.length + flights.length + hotels.length + properties.length + services.length;
  const totalActiveDeals = deals.filter(d => d.is_active).length + realEstateDeals + utilityDeals;

  const stats = [
    {
      title: 'Total Items Tracked',
      value: totalItems,
      icon: <Package size={24} />,
      subtitle: `${products.length} Products, ${flights.length + hotels.length} Travel, ${properties.length} Properties, ${services.length} Services`
    },
    {
      title: 'Active Deals',
      value: totalActiveDeals,
      icon: <Tag size={24} />,
      subtitle: 'Across all categories'
    },
    {
      title: 'Price Drops (Week)',
      value: alerts.filter(a => a.message.toLowerCase().includes('price drop')).length,
      icon: <TrendingDown size={24} />,
      subtitle: 'All categories'
    },
    {
      title: 'Unread Alerts',
      value: unreadCount,
      icon: <Bell size={24} />,
      subtitle: 'All categories'
    }
  ];

  const categoryStats = [
    { name: 'E-commerce', count: products.length, icon: <Package size={20} />, color: 'text-blue-400' },
    { name: 'Travel', count: flights.length + hotels.length, icon: <Plane size={20} />, color: 'text-green-400' },
    { name: 'Real Estate', count: properties.length, icon: <Home size={20} />, color: 'text-purple-400' },
    { name: 'Utilities', count: services.length, icon: <Zap size={20} />, color: 'text-yellow-400' }
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Dashboard</h1>
            <p className="text-zinc-400 mt-1">Welcome back! Here's your price tracking overview.</p>
          </div>
          <Button variant="primary" onClick={() => setShowAddModal(true)}>
            <Plus size={16} className="mr-2" />
            Add Product
          </Button>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <StatCard {...stat} />
            </motion.div>
          ))}
        </div>

        {/* Category Breakdown */}
        <Card>
          <h2 className="text-lg font-semibold text-white mb-4">Category Breakdown</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {categoryStats.map((category) => (
              <div key={category.name} className="text-center p-4 bg-gray-800/30 rounded-lg">
                <div className={`flex justify-center mb-2 ${category.color}`}>
                  {category.icon}
                </div>
                <div className="text-2xl font-bold text-white">{category.count}</div>
                <div className="text-sm text-gray-400">{category.name}</div>
              </div>
            ))}
          </div>
        </Card>

        {/* Recent Activity & Top Deals */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Activity */}
          <Card>
            <h2 className="text-lg font-semibold text-white mb-4">Recent Activity</h2>
            <div className="space-y-3">
              {alerts.length > 0 ? (
                alerts.slice(0, 5).map((alert) => (
                  <div key={alert.id} className="flex items-center space-x-3 p-3 bg-zinc-800/30 rounded-lg">
                    <div className="w-2 h-2 bg-accent rounded-full"></div>
                    <div className="flex-1 min-w-0">
                      <p className="text-white text-sm truncate">{alert.message}</p>
                      <p className="text-zinc-400 text-xs">
                        {new Date(alert.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8">
                  <Bell className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                  <p className="text-gray-400 text-sm">No recent activity</p>
                  <p className="text-gray-500 text-xs">Start tracking items to see alerts here</p>
                </div>
              )}
            </div>
          </Card>

          {/* Top Deals */}
          <Card>
            <h2 className="text-lg font-semibold text-white mb-4">Top Deals</h2>
            <div className="space-y-3">
              {deals.length > 0 ? (
                deals.slice(0, 5).map((deal) => (
                  <div key={deal.id} className="flex items-center justify-between p-3 bg-zinc-800/30 rounded-lg">
                    <div className="flex-1 min-w-0">
                      <p className="text-white text-sm truncate">{deal.product?.name}</p>
                      <p className="text-success text-xs">{deal.discount_percent}% off</p>
                    </div>
                    <div className="text-right">
                      <p className="text-white font-medium">₦{deal.deal_price.toLocaleString()}</p>
                      <p className="text-zinc-400 text-xs line-through">₦{deal.original_price.toLocaleString()}</p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8">
                  <Tag className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                  <p className="text-gray-400 text-sm">No deals available</p>
                  <p className="text-gray-500 text-xs">Deals will appear here when found</p>
                </div>
              )}
            </div>
          </Card>
        </div>

        {/* Modals */}
        <AddProductModal
          isOpen={showAddModal}
          onClose={() => setShowAddModal(false)}
        />
      </div>
    </DashboardLayout>
  );
};

export default Dashboard;