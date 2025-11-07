import { useState } from 'react';
import { motion } from 'framer-motion';
import { Link, Package } from 'lucide-react';
import { Modal } from '../common/Modal';
import { Input } from '../common/Input';
import { Button } from '../common/Button';
import { useProducts } from '../../hooks/useProducts';
import { useToast } from '../../hooks/useToast';
import type { CreateProductPayload } from '../../types';

interface AddProductModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AddProductModal = ({ isOpen, onClose }: AddProductModalProps) => {
  const [formData, setFormData] = useState<CreateProductPayload>({
    name: '',
    url: '',
    category: ''
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  
  const { addProduct } = useProducts();
  const { success: showSuccess, error: showError } = useToast();

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.url.trim()) {
      newErrors.url = 'URL is required';
    } else if (!isValidUrl(formData.url)) {
      newErrors.url = 'Please enter a valid URL';
    }

    if (!formData.name.trim()) {
      newErrors.name = 'Product name is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const isValidUrl = (url: string) => {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setIsLoading(true);

    try {
      await addProduct(formData);
      showSuccess('Product added successfully!');
      handleClose();
    } catch (err: any) {
      showError(err.message || 'Failed to add product');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    setFormData({ name: '', url: '', category: '' });
    setErrors({});
    onClose();
  };

  const handleChange = (field: keyof CreateProductPayload, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Add Product">
      <form onSubmit={handleSubmit} className="space-y-4">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Input
            label="Product URL"
            placeholder="https://example.com/product"
            value={formData.url}
            onChange={(e) => handleChange('url', e.target.value)}
            leftIcon={<Link size={16} />}
            error={errors.url}
            required
          />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Input
            label="Product Name"
            placeholder="Enter product name"
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
            leftIcon={<Package size={16} />}
            error={errors.name}
            required
          />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-2">
              Category (Optional)
            </label>
            <select
              value={formData.category}
              onChange={(e) => handleChange('category', e.target.value)}
              className="w-full px-4 py-3 bg-zinc-900/50 border border-zinc-700/50 rounded-lg text-white backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200"
            >
              <option value="">Select category</option>
              <option value="electronics">Electronics</option>
              <option value="clothing">Clothing</option>
              <option value="home">Home & Garden</option>
              <option value="books">Books</option>
              <option value="sports">Sports</option>
              <option value="other">Other</option>
            </select>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="flex space-x-3 pt-4"
        >
          <Button
            type="button"
            variant="ghost"
            onClick={handleClose}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            loading={isLoading}
            className="flex-1"
          >
            Add Product
          </Button>
        </motion.div>
      </form>
    </Modal>
  );
};