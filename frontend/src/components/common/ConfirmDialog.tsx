import type { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle } from 'lucide-react';
import { Modal } from './Modal';
import { Button } from './Button';

interface ConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'warning' | 'info';
  isLoading?: boolean;
}

export const ConfirmDialog = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  variant = 'danger',
  isLoading = false
}: ConfirmDialogProps) => {
  const handleConfirm = () => {
    onConfirm();
  };

  const getIcon = () => {
    switch (variant) {
      case 'danger':
        return <AlertTriangle className="w-6 h-6 text-danger" />;
      case 'warning':
        return <AlertTriangle className="w-6 h-6 text-warning" />;
      default:
        return <AlertTriangle className="w-6 h-6 text-accent" />;
    }
  };

  const getConfirmVariant = () => {
    switch (variant) {
      case 'danger':
        return 'danger' as const;
      case 'warning':
        return 'warning' as const;
      default:
        return 'primary' as const;
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.2 }}
        className="text-center"
      >
        <div className="flex justify-center mb-4">
          {getIcon()}
        </div>

        <h2 className="text-lg font-semibold text-white mb-2">{title}</h2>
        <p className="text-zinc-400 text-sm mb-6">{message}</p>

        <div className="flex space-x-3">
          <Button
            variant="ghost"
            onClick={onClose}
            disabled={isLoading}
            className="flex-1"
          >
            {cancelText}
          </Button>
          <Button
            variant={getConfirmVariant()}
            onClick={handleConfirm}
            loading={isLoading}
            className="flex-1"
          >
            {confirmText}
          </Button>
        </div>
      </motion.div>
    </Modal>
  );
};