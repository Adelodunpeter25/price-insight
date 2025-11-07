import { motion } from 'framer-motion';
import { Eye, X, ExternalLink } from 'lucide-react';
import type { Alert } from '../../types';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';

interface AlertItemProps {
  alert: Alert;
  onMarkAsRead: (id: number) => void;
  onDismiss: (id: number) => void;
  onViewProduct: (productId: number) => void;
}

const getAlertVariant = (type: string) => {
  switch (type) {
    case 'price_drop':
      return 'success';
    case 'deal_appeared':
      return 'info';
    case 'threshold':
      return 'warning';
    default:
      return 'info';
  }
};

export const AlertItem = ({ alert, onMarkAsRead, onDismiss, onViewProduct }: AlertItemProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card 
        className={`${!alert.is_read ? 'border-l-4 border-l-accent' : ''}`}
        hover={false}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2 mb-2">
              <Badge variant={getAlertVariant(alert.alert_type)} size="sm">
                {alert.alert_type.replace('_', ' ')}
              </Badge>
              {!alert.is_read && (
                <Badge variant="info" size="sm">New</Badge>
              )}
            </div>

            <p className="text-white text-sm mb-2">{alert.message}</p>

            <div className="flex items-center justify-between text-xs text-zinc-400">
              <span>{alert.product?.name || 'Unknown Product'}</span>
              <span>{new Date(alert.created_at).toLocaleDateString()}</span>
            </div>

            {alert.old_value && alert.new_value && (
              <div className="flex items-center space-x-2 mt-2 text-xs">
                <span className="text-zinc-400">₦{alert.old_value}</span>
                <span className="text-zinc-500">→</span>
                <span className="text-success font-medium">₦{alert.new_value}</span>
              </div>
            )}
          </div>

          <div className="flex space-x-1 ml-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onViewProduct(alert.product_id)}
            >
              <ExternalLink size={16} />
            </Button>
            
            {!alert.is_read && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onMarkAsRead(alert.id)}
              >
                <Eye size={16} />
              </Button>
            )}
            
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onDismiss(alert.id)}
            >
              <X size={16} />
            </Button>
          </div>
        </div>
      </Card>
    </motion.div>
  );
};