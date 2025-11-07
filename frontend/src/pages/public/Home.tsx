import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  TrendingDown, 
  Bell, 
  BarChart3,
  Shield,
  Globe,
  DollarSign
} from 'lucide-react';
import { PublicHeader, PublicFooter } from '../../components/layout';

const features = [
  {
    icon: TrendingDown,
    title: 'Price Tracking',
    description: 'Monitor prices across multiple categories and get notified of drops'
  },
  {
    icon: Bell,
    title: 'Smart Alerts',
    description: 'Receive instant notifications when prices hit your target'
  },
  {
    icon: BarChart3,
    title: 'Price History',
    description: 'View detailed price trends and make informed decisions'
  },
  {
    icon: Shield,
    title: 'Secure & Reliable',
    description: 'Your data is protected with enterprise-grade security'
  },
  {
    icon: Globe,
    title: 'Multi-Category',
    description: 'Track e-commerce, travel, real estate, and utility prices'
  },
  {
    icon: DollarSign,
    title: 'Currency Normalized',
    description: 'All prices converted to Nigerian Naira for easy comparison'
  }
];

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-900">
      <PublicHeader />

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center px-4 sm:px-6 lg:px-8">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-gray-900 to-purple-900/20"></div>
        
        {/* Animated background elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{animationDelay: '2s'}}></div>
        </div>
        
        <div className="relative max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="inline-flex items-center px-4 py-2 bg-blue-500/10 border border-blue-500/20 rounded-full text-blue-400 text-sm font-medium mb-8"
            >
              <span className="w-2 h-2 bg-blue-400 rounded-full mr-2 animate-pulse"></span>
              Live Price Monitoring Across Multiple Categories
            </motion.div>
            
            {/* Main heading */}
            <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold text-white mb-6 leading-tight">
              Track Prices,
              <br />
              <span className="bg-gradient-to-r from-blue-400 via-blue-500 to-purple-500 bg-clip-text text-transparent">
                Save Money
              </span>
            </h1>
            
            {/* Subtitle */}
            <p className="text-xl md:text-2xl text-gray-300 mb-12 max-w-4xl mx-auto leading-relaxed">
              Monitor prices across e-commerce, travel, real estate, and utilities. 
              Get instant alerts when prices drop and never miss a deal again.
            </p>
            
            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-6 justify-center mb-16">
              <Link 
                to="/signup"
                className="group bg-gradient-to-r from-blue-600 to-blue-700 text-white px-8 py-4 rounded-xl text-lg font-semibold hover:from-blue-700 hover:to-blue-800 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-blue-500/25"
              >
                <span className="flex items-center justify-center">
                  Start Tracking Free
                  <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </span>
              </Link>
              <Link 
                to="/about"
                className="group border-2 border-gray-600 text-white px-8 py-4 rounded-xl text-lg font-semibold hover:border-gray-500 hover:bg-gray-800/50 transition-all duration-300 backdrop-blur-sm"
              >
                <span className="flex items-center justify-center">
                  Learn More
                  <svg className="w-5 h-5 ml-2 group-hover:rotate-45 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </span>
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

      {/* FAQ Preview Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Frequently Asked Questions
            </h2>
            <p className="text-xl text-gray-300">
              Quick answers to common questions
            </p>
          </div>
          
          <div className="space-y-6">
            <div className="bg-gray-800/50 backdrop-blur-md border border-gray-700 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-2">
                Is Price Insight free to use?
              </h3>
              <p className="text-gray-300">
                Yes! Price Insight offers a free tier with basic price tracking and alerts. Premium plans are available for advanced features.
              </p>
            </div>
            
            <div className="bg-gray-800/50 backdrop-blur-md border border-gray-700 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-2">
                How accurate are the price alerts?
              </h3>
              <p className="text-gray-300">
                Our system checks prices multiple times per day with high accuracy. We recommend verifying prices on the retailer's website before purchasing.
              </p>
            </div>
            
            <div className="bg-gray-800/50 backdrop-blur-md border border-gray-700 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-2">
                What categories can I track?
              </h3>
              <p className="text-gray-300">
                You can track prices across e-commerce products, travel bookings, real estate properties, and utility services.
              </p>
            </div>
            
            <div className="bg-gray-800/50 backdrop-blur-md border border-gray-700 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-2">
                How do I set up price alerts?
              </h3>
              <p className="text-gray-300">
                Simply add a product URL, set your desired price threshold, and we'll notify you via email when the price drops.
              </p>
            </div>
          </div>
          
          <div className="text-center mt-8">
            <Link 
              to="/faq"
              className="text-blue-400 hover:text-blue-300 font-semibold"
            >
              View All FAQs →
            </Link>
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

      <PublicFooter />
    </div>
  );
}