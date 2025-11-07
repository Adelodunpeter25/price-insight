import { motion } from 'framer-motion';
import { ExternalLink, Trash2, TrendingDown, TrendingUp } from 'lucide-react';
import type { Product } from '../../types';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';

interface ProductCardProps {
  product: Product;
  onRemove: (id: number) => void;
  onView: (id: number) => void;
  priceChange?: number;
}

export const ProductCard = ({ product, onRemove, onView, priceChange }: ProductCardProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="h-full">
        <div className="flex flex-col h-full">
          <div className="flex items-start justify-between mb-3">
            <h3 className="text-white font-medium text-sm line-clamp-2 flex-1">
              {product.name}
            </h3>
            <Badge variant="info" size="sm" className="ml-2">
              {product.site}
            </Badge>
          </div>

          <div className="flex items-center space-x-2 mb-3">
            <span className="text-2xl font-bold text-white">₦0</span>
            {priceChange !== undefined && (
              <div className={`flex items-center text-sm ${
                priceChange >= 0 ? 'text-success' : 'text-danger'
              }`}>
                {priceChange >= 0 ? (
                  <TrendingUp size={16} className="mr-1" />
                ) : (
                  <TrendingDown size={16} className="mr-1" />
                )}
                <span>{Math.abs(priceChange)}%</span>
              </div>
            )}
          </div>

          {product.category && (
            <p className="text-zinc-400 text-xs mb-4">{product.category}</p>
          )}

          <div className="flex space-x-2 mt-auto">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onView(product.id)}
              className="flex-1"
            >
              <ExternalLink size={16} className="mr-1" />
              View
            </Button>
            <Button
              variant="danger"
              size="sm"
              onClick={() => onRemove(product.id)}
            >
              <Trash2 size={16} />
            </Button>
          </div>
        </div>
      </Card>
    </motion.div>
  );
};