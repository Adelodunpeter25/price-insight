import { motion } from 'framer-motion';
import { ExternalLink, Trash2, TrendingDown, TrendingUp } from 'lucide-react';
import type { Product } from '../../types';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';

interface ProductTableProps {
  products: Product[];
  onRemove: (id: number) => void;
  onView: (id: number) => void;
}

export const ProductTable = ({ products, onRemove, onView }: ProductTableProps) => {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-zinc-800">
            <th className="text-left py-3 px-4 text-zinc-400 font-medium">Product</th>
            <th className="text-left py-3 px-4 text-zinc-400 font-medium">Current Price</th>
            <th className="text-left py-3 px-4 text-zinc-400 font-medium">Change</th>
            <th className="text-left py-3 px-4 text-zinc-400 font-medium">Site</th>
            <th className="text-right py-3 px-4 text-zinc-400 font-medium">Actions</th>
          </tr>
        </thead>
        <tbody>
          {products.map((product, index) => (
            <motion.tr
              key={product.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className="border-b border-zinc-800/50 hover:bg-zinc-900/30 transition-colors"
            >
              <td className="py-4 px-4">
                <div>
                  <p className="text-white font-medium text-sm line-clamp-1">
                    {product.name}
                  </p>
                  {product.category && (
                    <p className="text-zinc-400 text-xs mt-1">{product.category}</p>
                  )}
                </div>
              </td>
              
              <td className="py-4 px-4">
                <span className="text-white font-semibold">₦0</span>
              </td>
              
              <td className="py-4 px-4">
                <div className="flex items-center text-sm text-zinc-400">
                  <TrendingUp size={16} className="mr-1" />
                  <span>--</span>
                </div>
              </td>
              
              <td className="py-4 px-4">
                <Badge variant="info" size="sm">
                  {product.site}
                </Badge>
              </td>
              
              <td className="py-4 px-4">
                <div className="flex justify-end space-x-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onView(product.id)}
                  >
                    <ExternalLink size={16} />
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => onRemove(product.id)}
                  >
                    <Trash2 size={16} />
                  </Button>
                </div>
              </td>
            </motion.tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};