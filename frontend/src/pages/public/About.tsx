import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

export default function About() {
  return (
    <div className="min-h-screen bg-gray-900">
      {/* Navigation */}
      <nav className="bg-gray-900/80 backdrop-blur-md border-b border-gray-800 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="text-xl font-bold text-white">Price Insight</Link>
            <div className="flex items-center space-x-4">
              <Link to="/" className="text-gray-300 hover:text-white transition-colors">Home</Link>
              <Link to="/contact" className="text-gray-300 hover:text-white transition-colors">Contact</Link>
              <Link to="/login" className="text-gray-300 hover:text-white transition-colors">Login</Link>
              <Link to="/signup" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">Sign Up</Link>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl font-bold text-white mb-8">About Price Insight</h1>
          
          <div className="prose prose-invert max-w-none">
            <p className="text-xl text-gray-300 mb-8">
              Price Insight is a comprehensive price tracking platform that helps you monitor prices across multiple categories and never miss a deal again.
            </p>

            <h2 className="text-2xl font-semibold text-white mb-4">Our Mission</h2>
            <p className="text-gray-300 mb-6">
              We believe everyone deserves to make informed purchasing decisions. Our platform empowers users to track prices across e-commerce, travel, real estate, and utilities, ensuring you always get the best value for your money.
            </p>

            <h2 className="text-2xl font-semibold text-white mb-4">What We Track</h2>
            <ul className="text-gray-300 mb-6 space-y-2">
              <li><strong>E-commerce:</strong> Products from major online retailers</li>
              <li><strong>Travel:</strong> Flight prices and hotel rates</li>
              <li><strong>Real Estate:</strong> Property prices and rental rates</li>
              <li><strong>Utilities:</strong> Service plans and subscription prices</li>
            </ul>

            <h2 className="text-2xl font-semibold text-white mb-4">Key Features</h2>
            <ul className="text-gray-300 mb-6 space-y-2">
              <li>Real-time price monitoring with intelligent alerts</li>
              <li>Historical price data and trend analysis</li>
              <li>Currency normalization to Nigerian Naira</li>
              <li>Customizable alert thresholds</li>
              <li>Comprehensive deal detection</li>
              <li>Export capabilities for data analysis</li>
            </ul>

            <h2 className="text-2xl font-semibold text-white mb-4">Why Choose Us?</h2>
            <p className="text-gray-300 mb-6">
              Price Insight combines advanced web scraping technology with intelligent data analysis to provide you with accurate, up-to-date pricing information. Our platform is designed with security and reliability in mind, ensuring your data is always protected.
            </p>

            <div className="bg-gray-800/50 backdrop-blur-md border border-gray-700 rounded-xl p-6 mt-8">
              <h3 className="text-xl font-semibold text-white mb-4">Ready to Start Saving?</h3>
              <p className="text-gray-300 mb-4">
                Join thousands of users who are already making smarter purchasing decisions with Price Insight.
              </p>
              <Link 
                to="/signup"
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors inline-block"
              >
                Get Started Free
              </Link>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}