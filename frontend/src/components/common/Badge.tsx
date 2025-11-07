import type { ReactNode } from 'react';

interface BadgeProps {
  children: ReactNode;
  variant?: 'success' | 'danger' | 'warning' | 'info';
  size?: 'sm' | 'md';
  className?: string;
}

export const Badge = ({ 
  children, 
  variant = 'info', 
  size = 'sm',
  className = '' 
}: BadgeProps) => {
  const variants = {
    success: 'bg-success/20 text-success border-success/30',
    danger: 'bg-danger/20 text-danger border-danger/30',
    warning: 'bg-warning/20 text-warning border-warning/30',
    info: 'bg-accent/20 text-accent border-accent/30'
  };

  const sizes = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm'
  };

  return (
    <span className={`
      inline-flex items-center font-medium rounded-full border backdrop-blur-sm
      ${variants[variant]} ${sizes[size]} ${className}
    `}>
      {children}
    </span>
  );
};