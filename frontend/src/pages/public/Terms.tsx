import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

export default function Terms() {
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
          <h1 className="text-4xl font-bold text-white mb-8">Terms of Service</h1>
          <p className="text-gray-400 mb-8">Last updated: December 2024</p>
          
          <div className="prose prose-invert max-w-none space-y-8">
            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">1. Acceptance of Terms</h2>
              <p className="text-gray-300 mb-4">
                By accessing and using Price Insight, you accept and agree to be bound by the terms 
                and provision of this agreement. If you do not agree to abide by the above, please 
                do not use this service.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">2. Description of Service</h2>
              <p className="text-gray-300 mb-4">
                Price Insight is a price tracking and monitoring service that helps users track 
                prices across various categories including e-commerce, travel, real estate, and utilities.
              </p>
              <ul className="text-gray-300 space-y-2 ml-6">
                <li>Real-time price monitoring and alerts</li>
                <li>Historical price data and analytics</li>
                <li>Deal detection and notifications</li>
                <li>Data export capabilities</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">3. User Accounts</h2>
              <p className="text-gray-300 mb-4">
                To use certain features of our service, you must create an account:
              </p>
              <ul className="text-gray-300 space-y-2 ml-6">
                <li>You must provide accurate and complete information</li>
                <li>You are responsible for maintaining account security</li>
                <li>You must notify us immediately of any unauthorized use</li>
                <li>One account per person or entity</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">4. Acceptable Use</h2>
              <p className="text-gray-300 mb-4">
                You agree to use Price Insight only for lawful purposes and in accordance with these terms:
              </p>
              <ul className="text-gray-300 space-y-2 ml-6">
                <li>Do not use the service for any illegal or unauthorized purpose</li>
                <li>Do not attempt to gain unauthorized access to our systems</li>
                <li>Do not interfere with or disrupt the service</li>
                <li>Do not use automated tools to access the service excessively</li>
                <li>Do not share your account credentials with others</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">5. Price Data Accuracy</h2>
              <p className="text-gray-300 mb-4">
                While we strive to provide accurate price information:
              </p>
              <ul className="text-gray-300 space-y-2 ml-6">
                <li>Prices are obtained from third-party sources and may not be real-time</li>
                <li>We do not guarantee the accuracy of price data</li>
                <li>Always verify prices on the retailer's website before purchasing</li>
                <li>We are not responsible for pricing errors or discrepancies</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">6. Subscription and Billing</h2>
              <p className="text-gray-300 mb-4">
                For premium features:
              </p>
              <ul className="text-gray-300 space-y-2 ml-6">
                <li>Subscriptions are billed in advance on a monthly or annual basis</li>
                <li>You can cancel your subscription at any time</li>
                <li>Refunds are provided according to our refund policy</li>
                <li>Price changes will be communicated 30 days in advance</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">7. Intellectual Property</h2>
              <p className="text-gray-300 mb-4">
                The service and its original content, features, and functionality are owned by 
                Price Insight and are protected by international copyright, trademark, and other laws.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">8. Privacy Policy</h2>
              <p className="text-gray-300 mb-4">
                Your privacy is important to us. Please review our Privacy Policy, which also 
                governs your use of the service, to understand our practices.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">9. Disclaimers</h2>
              <p className="text-gray-300 mb-4">
                The service is provided "as is" without warranties of any kind:
              </p>
              <ul className="text-gray-300 space-y-2 ml-6">
                <li>We do not warrant that the service will be uninterrupted or error-free</li>
                <li>We do not guarantee the accuracy or completeness of information</li>
                <li>We are not responsible for third-party content or services</li>
                <li>Use of the service is at your own risk</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">10. Limitation of Liability</h2>
              <p className="text-gray-300 mb-4">
                In no event shall Price Insight be liable for any indirect, incidental, special, 
                consequential, or punitive damages, including without limitation, loss of profits, 
                data, use, goodwill, or other intangible losses.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">11. Termination</h2>
              <p className="text-gray-300 mb-4">
                We may terminate or suspend your account and access to the service immediately, 
                without prior notice, for conduct that we believe violates these terms or is 
                harmful to other users, us, or third parties.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">12. Changes to Terms</h2>
              <p className="text-gray-300 mb-4">
                We reserve the right to modify these terms at any time. We will notify users of 
                any material changes. Your continued use of the service after such modifications 
                constitutes acceptance of the updated terms.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">13. Governing Law</h2>
              <p className="text-gray-300 mb-4">
                These terms shall be governed by and construed in accordance with the laws of 
                Nigeria, without regard to its conflict of law provisions.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">14. Contact Information</h2>
              <p className="text-gray-300 mb-4">
                If you have any questions about these Terms of Service, please contact us:
              </p>
              <ul className="text-gray-300 space-y-2 ml-6">
                <li>Email: legal@priceinsight.com</li>
                <li>Phone: +234 (0) 123 456 7890</li>
                <li>Address: Lagos, Nigeria</li>
              </ul>
            </section>
          </div>

          <div className="mt-12 p-6 bg-gray-800/50 backdrop-blur-md border border-gray-700 rounded-xl">
            <h3 className="text-lg font-semibold text-white mb-2">Questions about our terms?</h3>
            <p className="text-gray-300 mb-4">
              If you have any questions about these terms of service, please contact our legal team.
            </p>
            <Link 
              to="/contact"
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors inline-block"
            >
              Contact Us
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
}