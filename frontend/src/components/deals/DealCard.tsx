import { motion } from 'framer-motion';
import { ExternalLink, Bell, Clock } from 'lucide-react';
import type { Deal } from '../../types';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';

interface DealCardProps {
  deal: Deal;
  onView: (id: number) => void;
  onAddAlert: (productId: number) => void;
}

export const DealCard = ({ deal, onView, onAddAlert }: DealCardProps) => {
  const getUrgencyColor = (endDate?: string) => {
    if (!endDate) return 'info';
    
    const now = new Date();
    const end = new Date(endDate);
    const daysLeft = Math.ceil((end.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    
    if (daysLeft < 1) return 'danger';
    if (daysLeft <= 7) return 'warning';
    return 'success';
  };

  const formatTimeLeft = (endDate?: string) => {
    if (!endDate) return 'No expiry';
    
    const now = new Date();
    const end = new Date(endDate);
    const diff = end.getTime() - now.getTime();
    
    if (diff <= 0) return 'Expired';
    
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    
    if (days > 0) return `${days}d ${hours}h left`;
    return `${hours}h left`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="h-full">
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-start justify-between mb-3">
            <Badge 
              variant={getUrgencyColor(deal.deal_end_date)} 
              size="sm"
            >
              {deal.discount_percent}% OFF
            </Badge>
            <Badge variant="info" size="sm">
              {deal.deal_type}
            </Badge>
          </div>

          {/* Product name */}
          <h3 className="text-white font-medium text-sm line-clamp-2 mb-3">
            {deal.product?.name || 'Product Name'}
          </h3>

          {/* Pricing */}
          <div className="mb-3">
            <div className="flex items-center space-x-2">
              <span className="text-zinc-400 text-sm line-through">
                ₦{deal.original_price.toLocaleString()}
              </span>
              <span className="text-success text-lg font-bold">
                ₦{deal.deal_price.toLocaleString()}
              </span>
            </div>
          </div>

          {/* Description */}
          {deal.description && (
            <p className="text-zinc-400 text-xs mb-3 line-clamp-2">
              {deal.description}
            </p>
          )}

          {/* Time left */}
          <div className="flex items-center text-zinc-400 text-xs mb-4">
            <Clock size={14} className="mr-1" />
            <span>{formatTimeLeft(deal.deal_end_date)}</span>
          </div>

          {/* Actions */}
          <div className="flex space-x-2 mt-auto">
            <Button
              variant="primary"
              size="sm"
              onClick={() => onView(deal.product_id)}
              className="flex-1"
            >
              <ExternalLink size={16} className="mr-1" />
              View Deal
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onAddAlert(deal.product_id)}
            >
              <Bell size={16} />
            </Button>
          </div>
        </div>
      </Card>
    </motion.div>
  );
};