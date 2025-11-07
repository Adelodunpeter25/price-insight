import type { ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react';
import type { Toast as ToastType } from '../../hooks/useToast';

interface ToastProps {
  toast: ToastType;
  onRemove: (id: string) => void;
}

const icons = {
  success: CheckCircle,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info
};

const variants = {
  success: 'bg-success/20 border-success/30 text-success',
  error: 'bg-danger/20 border-danger/30 text-danger',
  warning: 'bg-warning/20 border-warning/30 text-warning',
  info: 'bg-accent/20 border-accent/30 text-accent'
};

export const Toast = ({ toast, onRemove }: ToastProps) => {
  const Icon = icons[toast.variant];

  return (
    <motion.div
      initial={{ opacity: 0, x: 300, scale: 0.3 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: 300, scale: 0.5 }}
      transition={{ duration: 0.3 }}
      className={`
        flex items-start space-x-3 p-4 rounded-lg border backdrop-blur-sm
        ${variants[toast.variant]} max-w-sm w-full shadow-lg
      `}
    >
      <Icon size={20} className="flex-shrink-0 mt-0.5" />
      
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-white">{toast.message}</p>
        {toast.action && (
          <button
            onClick={toast.action.onClick}
            className="mt-2 text-xs font-medium underline hover:no-underline"
          >
            {toast.action.label}
          </button>
        )}
      </div>
      
      <button
        onClick={() => onRemove(toast.id)}
        className="flex-shrink-0 text-zinc-400 hover:text-white transition-colors"
      >
        <X size={16} />
      </button>
    </motion.div>
  );
};

interface ToastContainerProps {
  toasts: ToastType[];
  onRemove: (id: string) => void;
}

export const ToastContainer = ({ toasts, onRemove }: ToastContainerProps) => {
  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      <AnimatePresence>
        {toasts.map(toast => (
          <Toast key={toast.id} toast={toast} onRemove={onRemove} />
        ))}
      </AnimatePresence>
    </div>
  );
};