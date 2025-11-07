import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Mail, ArrowLeft } from 'lucide-react';
import { useToast } from '../../hooks/useToast';
import { AuthLayout } from '../../components/layout/AuthLayout';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';

export const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const { success: showSuccess, error: showError } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      setIsSubmitted(true);
      showSuccess('Password reset instructions sent to your email');
    } catch (err) {
      showError('Failed to send reset instructions');
    } finally {
      setIsLoading(false);
    }
  };

  if (isSubmitted) {
    return (
      <AuthLayout>
        <div className="bg-gray-800/50 backdrop-blur-md border border-gray-700 rounded-xl p-8 max-w-md mx-auto relative">
          <Link
            to="/"
            className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors flex items-center gap-1 text-sm"
          >
            <ArrowLeft size={16} />
            Home
          </Link>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
            className="text-center"
          >
            <div className="w-16 h-16 bg-success/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <Mail className="w-8 h-8 text-success" />
            </div>
            
            <h1 className="text-2xl font-bold text-white mb-2">Check Your Email</h1>
            <p className="text-zinc-400 text-sm mb-6">
              We've sent password reset instructions to <br />
              <span className="text-white">{email}</span>
            </p>

            <Link
              to="/login"
              className="inline-flex items-center text-accent hover:text-accent/80 text-sm transition-colors"
            >
              <ArrowLeft size={16} className="mr-1" />
              Back to login
            </Link>
          </motion.div>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout>
      <div className="bg-gray-800/50 backdrop-blur-md border border-gray-700 rounded-xl p-8 max-w-md mx-auto relative">
        <Link
          to="/"
          className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors flex items-center gap-1 text-sm"
        >
          <ArrowLeft size={16} />
          Home
        </Link>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <div className="text-center mb-6">
            <h1 className="text-2xl font-bold text-white mb-2">Forgot Password</h1>
            <p className="text-zinc-400 text-sm">
              Enter your email and we'll send you reset instructions
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
            >
              <Input
                type="email"
                label="Email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                leftIcon={<Mail size={16} />}
                required
              />
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Button
                type="submit"
                variant="primary"
                size="lg"
                loading={isLoading}
                className="w-full"
              >
                Send Reset Instructions
              </Button>
            </motion.div>
          </form>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="mt-6 text-center"
          >
            <Link
              to="/login"
              className="inline-flex items-center text-accent hover:text-accent/80 text-sm transition-colors"
            >
              <ArrowLeft size={16} className="mr-1" />
              Back to login
            </Link>
          </motion.div>
        </motion.div>
      </div>
    </AuthLayout>
  );
};