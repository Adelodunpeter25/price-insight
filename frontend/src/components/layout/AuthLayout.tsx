import type { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuthContext } from '../../context/AuthContext';

interface AuthLayoutProps {
  children: ReactNode;
}

export const AuthLayout = ({ children }: AuthLayoutProps) => {
  const { isAuthenticated, isLoading } = useAuthContext();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent"></div>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        {/* Branding */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center space-x-2 mb-4">
            <div className="w-10 h-10 bg-accent rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-lg">P</span>
            </div>
            <span className="text-white font-bold text-xl">Price Insight</span>
          </div>
          <p className="text-zinc-400 text-sm">
            Smart price tracking across multiple categories
          </p>
        </div>

        {/* Auth form */}
        <div className="glass-card rounded-xl p-6">
          {children}
        </div>

        {/* Footer */}
        <p className="text-center text-zinc-500 text-xs mt-6">
          © 2024 Price Insight. All rights reserved.
        </p>
      </motion.div>
    </div>
  );
};