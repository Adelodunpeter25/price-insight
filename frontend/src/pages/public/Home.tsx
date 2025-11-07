import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  TrendingDownIcon, 
  BellIcon, 
  ChartBarIcon,
  ShieldCheckIcon,
  GlobeAltIcon,
  CurrencyDollarIcon
} from '@heroicons/react/24/outline';

const features = [
  {
    icon: TrendingDownIcon,
    title: 'Price Tracking',
    description: 'Monitor prices across multiple categories and get notified of drops'
  },
  {
    icon: BellIcon,
    title: 'Smart Alerts',
    description: 'Receive instant notifications when prices hit your target'
  },
  {
    icon: ChartBarIcon,
    title: 'Price History',
    description: 'View detailed price trends and make informed decisions'
  },
  {
    icon: ShieldCheckIcon,
    title: 'Secure & Reliable',
    description: 'Your data is protected with enterprise-grade security'
  },
  {
    icon: GlobeAltIcon,
    title: 'Multi-Category',
    description: 'Track e-commerce, travel, real estate, and utility prices'
  },
  {
    icon: CurrencyDollarIcon,
    title: 'Currency Normalized',
    description: 'All prices converted to Nigerian Naira for easy comparison'
  }
];

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-900">
      {/* Navigation */}
      <nav className="bg-gray-900/80 backdrop-blur-md border-b border-gray-800 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-white">Price Insight</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Link 
                to="/about" 
                className="text-gray-300 hover:text-white transition-colors"
              >
                About
              </Link>
              <Link 
                to="/contact" 
                className="text-gray-300 hover:text-white transition-colors"
              >
                Contact
              </Link>
              <Link 
                to="/login" 
                className="text-gray-300 hover:text-white transition-colors"
              >
                Login
              </Link>
              <Link 
                to="/signup" 
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Sign Up
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
              Track Prices,
              <span className="text-blue-400"> Save Money</span>
            </h1>
            <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
              Monitor prices across e-commerce, travel, real estate, and utilities. 
              Get instant alerts when prices drop and never miss a deal again.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link 
                to="/signup"
                className="bg-blue-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-blue-700 transition-colors"
              >
                Start Tracking Free
              </Link>
              <Link 
                to="/about"
                className="border border-gray-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-gray-800 transition-colors"
              >
                Learn More
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Why Choose Price Insight?
            </h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Comprehensive price tracking with intelligent alerts and detailed analytics
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="bg-gray-900/50 backdrop-blur-md border border-gray-700 rounded-xl p-6 hover:border-gray-600 transition-colors"
              >
                <feature.icon className="h-12 w-12 text-blue-400 mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-300">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
              Ready to Start Saving?
            </h2>
            <p className="text-xl text-gray-300 mb-8">
              Join thousands of users who are already saving money with Price Insight
            </p>
            <Link 
              to="/signup"
              className="bg-blue-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-blue-700 transition-colors inline-block"
            >
              Get Started Today
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 border-t border-gray-800 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-lg font-semibold text-white mb-4">Price Insight</h3>
              <p className="text-gray-400">
                Smart price tracking for smarter shopping decisions.
              </p>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-white mb-4">Product</h4>
              <ul className="space-y-2">
                <li><Link to="/about" className="text-gray-400 hover:text-white">About</Link></li>
                <li><Link to="/contact" className="text-gray-400 hover:text-white">Contact</Link></li>
                <li><Link to="/faq" className="text-gray-400 hover:text-white">FAQ</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-white mb-4">Legal</h4>
              <ul className="space-y-2">
                <li><Link to="/privacy" className="text-gray-400 hover:text-white">Privacy Policy</Link></li>
                <li><Link to="/terms" className="text-gray-400 hover:text-white">Terms of Service</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-white mb-4">Account</h4>
              <ul className="space-y-2">
                <li><Link to="/login" className="text-gray-400 hover:text-white">Login</Link></li>
                <li><Link to="/signup" className="text-gray-400 hover:text-white">Sign Up</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center">
            <p className="text-gray-400">
              © 2024 Price Insight. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}