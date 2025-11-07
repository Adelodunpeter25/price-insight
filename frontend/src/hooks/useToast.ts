import { useState, useCallback } from 'react';

export interface Toast {
  id: string;
  message: string;
  variant: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export const useToast = () => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((toast: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newToast = { ...toast, id };
    
    setToasts(prev => [...prev, newToast]);

    // Auto-dismiss after duration
    const duration = toast.duration || 5000;
    setTimeout(() => {
      removeToast(id);
    }, duration);

    return id;
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  const success = useCallback((message: string, options?: Partial<Toast>) => {
    return addToast({ ...options, message, variant: 'success' });
  }, [addToast]);

  const error = useCallback((message: string, options?: Partial<Toast>) => {
    return addToast({ ...options, message, variant: 'error' });
  }, [addToast]);

  const warning = useCallback((message: string, options?: Partial<Toast>) => {
    return addToast({ ...options, message, variant: 'warning' });
  }, [addToast]);

  const info = useCallback((message: string, options?: Partial<Toast>) => {
    return addToast({ ...options, message, variant: 'info' });
  }, [addToast]);

  return {
    toasts,
    addToast,
    removeToast,
    success,
    error,
    warning,
    info
  };
};