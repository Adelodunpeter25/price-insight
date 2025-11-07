import { motion } from 'framer-motion';
import type { Deal } from '../../types';
import { DealCard } from './DealCard';

interface DealGridProps {
  deals: Deal[];
  onView: (id: number) => void;
  onAddAlert: (productId: number) => void;
}

export const DealGrid = ({ deals, onView, onAddAlert }: DealGridProps) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {deals.map((deal, index) => (
        <motion.div
          key={deal.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: index * 0.1 }}
        >
          <DealCard
            deal={deal}
            onView={onView}
            onAddAlert={onAddAlert}
          />
        </motion.div>
      ))}
    </div>
  );
};