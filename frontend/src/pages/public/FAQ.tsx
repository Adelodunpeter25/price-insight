import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ChevronDownIcon } from '@heroicons/react/24/outline';

const faqs = [
  {
    question: 'How does Price Insight track prices?',
    answer: 'We use advanced web scraping technology to monitor prices across multiple platforms in real-time. Our system checks prices regularly and alerts you when there are changes or deals that match your criteria.'
  },
  {
    question: 'Is Price Insight free to use?',
    answer: 'Yes! Price Insight offers a free tier that includes basic price tracking and alerts. We also offer premium plans with advanced features like unlimited tracking, detailed analytics, and priority support.'
  },
  {
    question: 'How accurate are the price alerts?',
    answer: 'Our price tracking is highly accurate, with updates occurring multiple times per day. However, prices can change rapidly on some platforms, so we recommend verifying the current price on the retailer\'s website before making a purchase.'
  },
  {
    question: 'What categories can I track?',
    answer: 'Price Insight supports tracking across four main categories: E-commerce products, Travel (flights and hotels), Real Estate properties, and Utilities/Subscriptions. Each category has specialized tracking features.'
  },
  {
    question: 'How do I set up price alerts?',
    answer: 'After adding a product to track, you can set custom alert thresholds. Choose from price drop alerts, target price alerts, or deal detection alerts. You\'ll receive notifications via email when your conditions are met.'
  },
  {
    question: 'Can I export my price data?',
    answer: 'Yes! Premium users can export their price tracking data in PDF or CSV format for analysis. This includes historical price data, deal summaries, and alert history.'
  },
  {
    question: 'Is my data secure?',
    answer: 'Absolutely. We use enterprise-grade security measures including encryption, secure authentication, and regular security audits. We never store your payment information or share your data with third parties.'
  },
  {
    question: 'How often are prices updated?',
    answer: 'Price updates vary by category and platform. E-commerce prices are typically updated every 2-4 hours, travel prices every 6-12 hours, and real estate/utilities daily or weekly depending on the source.'
  },
  {
    question: 'Can I track international prices?',
    answer: 'Yes, but all prices are automatically converted to Nigerian Naira for easy comparison. We support tracking from major international retailers and platforms.'
  },
  {
    question: 'What if a website blocks price tracking?',
    answer: 'Some websites may implement anti-scraping measures. When this happens, we work to adapt our tracking methods while respecting the website\'s terms of service. We\'ll notify you if tracking becomes unavailable for a specific product.'
  }
];

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const toggleFAQ = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Navigation */}
      <nav className="bg-gray-900/80 backdrop-blur-md border-b border-gray-800 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="text-xl font-bold text-white">Price Insight</Link>
            <div className="flex items-center space-x-4">
              <Link to="/" className="text-gray-300 hover:text-white transition-colors">Home</Link>
              <Link to="/about" className="text-gray-300 hover:text-white transition-colors">About</Link>
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
          <div className="text-center mb-16">
            <h1 className="text-4xl font-bold text-white mb-4">Frequently Asked Questions</h1>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Find answers to common questions about Price Insight and how it works.
            </p>
          </div>

          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.05 }}
                className="bg-gray-800/50 backdrop-blur-md border border-gray-700 rounded-xl overflow-hidden"
              >
                <button
                  onClick={() => toggleFAQ(index)}
                  className="w-full px-6 py-4 text-left flex justify-between items-center hover:bg-gray-700/30 transition-colors"
                >
                  <h3 className="text-lg font-semibold text-white pr-4">
                    {faq.question}
                  </h3>
                  <ChevronDownIcon 
                    className={`h-5 w-5 text-gray-400 transition-transform ${
                      openIndex === index ? 'rotate-180' : ''
                    }`}
                  />
                </button>
                
                {openIndex === index && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="px-6 pb-4"
                  >
                    <p className="text-gray-300 leading-relaxed">
                      {faq.answer}
                    </p>
                  </motion.div>
                )}
              </motion.div>
            ))}
          </div>

          <div className="mt-16 text-center">
            <div className="bg-gray-800/50 backdrop-blur-md border border-gray-700 rounded-xl p-8">
              <h2 className="text-2xl font-semibold text-white mb-4">
                Still have questions?
              </h2>
              <p className="text-gray-300 mb-6">
                Can't find the answer you're looking for? Our support team is here to help.
              </p>
              <Link 
                to="/contact"
                className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors inline-block"
              >
                Contact Support
              </Link>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}