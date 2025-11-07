import { motion } from 'framer-motion';
import { Package, Tag, Bell, TrendingDown, Plus } from 'lucide-react';
import { DashboardLayout } from '../components/layout/DashboardLayout';
import { StatCard } from '../components/dashboard/StatCard';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import { useProducts } from '../hooks/useProducts';
import { useDeals } from '../hooks/useDeals';
import { useAlerts } from '../hooks/useAlerts';

export const Dashboard = () => {
  const { products } = useProducts();
  const { deals } = useDeals();
  const { alerts, unreadCount } = useAlerts();

  const stats = [
    {
      title: 'Total Products',
      value: products.length,
      icon: <Package size={24} />,
      trend: { value: 12, isPositive: true }
    },
    {
      title: 'Active Deals',
      value: deals.filter(d => d.is_active).length,
      icon: <Tag size={24} />,
      trend: { value: 8, isPositive: true }
    },
    {
      title: 'Price Drops (Week)',
      value: 5,
      icon: <TrendingDown size={24} />,
      trend: { value: 25, isPositive: true }
    },
    {
      title: 'Unread Alerts',
      value: unreadCount,
      icon: <Bell size={24} />
    }
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
          <Button variant="primary">
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

        {/* Recent Activity & Top Deals */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Activity */}
          <Card>
            <h2 className="text-lg font-semibold text-white mb-4">Recent Activity</h2>
            <div className="space-y-3">
              {alerts.slice(0, 5).map((alert) => (
                <div key={alert.id} className="flex items-center space-x-3 p-3 bg-zinc-800/30 rounded-lg">
                  <div className="w-2 h-2 bg-accent rounded-full"></div>
                  <div className="flex-1 min-w-0">
                    <p className="text-white text-sm truncate">{alert.message}</p>
                    <p className="text-zinc-400 text-xs">
                      {new Date(alert.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* Top Deals */}
          <Card>
            <h2 className="text-lg font-semibold text-white mb-4">Top Deals</h2>
            <div className="space-y-3">
              {deals.slice(0, 5).map((deal) => (
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
              ))}
            </div>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
};