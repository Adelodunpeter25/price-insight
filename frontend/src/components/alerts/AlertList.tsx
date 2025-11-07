import { motion } from 'framer-motion';
import type { Alert } from '../../types';
import { AlertItem } from './AlertItem';
import { Button } from '../common/Button';

interface AlertListProps {
  alerts: Alert[];
  onMarkAsRead: (id: number) => void;
  onDismiss: (id: number) => void;
  onViewProduct: (productId: number) => void;
  onMarkAllAsRead: () => void;
  hasUnread: boolean;
}

export const AlertList = ({ 
  alerts, 
  onMarkAsRead, 
  onDismiss, 
  onViewProduct, 
  onMarkAllAsRead,
  hasUnread 
}: AlertListProps) => {
  return (
    <div className="space-y-4">
      {hasUnread && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex justify-end"
        >
          <Button variant="ghost" size="sm" onClick={onMarkAllAsRead}>
            Mark all as read
          </Button>
        </motion.div>
      )}

      <div className="space-y-3">
        {alerts.map((alert, index) => (
          <motion.div
            key={alert.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
          >
            <AlertItem
              alert={alert}
              onMarkAsRead={onMarkAsRead}
              onDismiss={onDismiss}
              onViewProduct={onViewProduct}
            />
          </motion.div>
        ))}
      </div>

      {alerts.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <p className="text-zinc-400">No alerts to display</p>
        </motion.div>
      )}
    </div>
  );
};