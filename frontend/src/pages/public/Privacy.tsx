import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { PublicHeader, PublicFooter } from '../../components/layout';

export default function Privacy() {
  return (
    <div className="min-h-screen bg-gray-900">
      <PublicHeader />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl font-bold text-white mb-8">Privacy Policy</h1>
          <p className="text-gray-400 mb-8">Last updated: December 2024</p>
          
          <div className="prose prose-invert max-w-none space-y-8">
            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">1. Information We Collect</h2>
              <p className="text-gray-300 mb-4">
                We collect information you provide directly to us, such as when you create an account, 
                add products to track, or contact us for support.
              </p>
              <ul className="text-gray-300 space-y-2 ml-6">
                <li>Account information (name, email address, password)</li>
                <li>Product URLs and tracking preferences</li>
                <li>Alert settings and notification preferences</li>
                <li>Usage data and analytics</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">2. How We Use Your Information</h2>
              <p className="text-gray-300 mb-4">
                We use the information we collect to provide, maintain, and improve our services:
              </p>
              <ul className="text-gray-300 space-y-2 ml-6">
                <li>Track prices for products you've added</li>
                <li>Send price alerts and notifications</li>
                <li>Provide customer support</li>
                <li>Improve our price tracking algorithms</li>
                <li>Ensure security and prevent fraud</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">3. Information Sharing</h2>
              <p className="text-gray-300 mb-4">
                We do not sell, trade, or otherwise transfer your personal information to third parties. 
                We may share information in the following circumstances:
              </p>
              <ul className="text-gray-300 space-y-2 ml-6">
                <li>With your consent</li>
                <li>To comply with legal obligations</li>
                <li>To protect our rights and prevent fraud</li>
                <li>With service providers who assist in our operations</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">4. Data Security</h2>
              <p className="text-gray-300 mb-4">
                We implement appropriate security measures to protect your personal information:
              </p>
              <ul className="text-gray-300 space-y-2 ml-6">
                <li>Encryption of data in transit and at rest</li>
                <li>Secure authentication and access controls</li>
                <li>Regular security audits and monitoring</li>
                <li>Limited access to personal information</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">5. Your Rights</h2>
              <p className="text-gray-300 mb-4">
                You have the following rights regarding your personal information:
              </p>
              <ul className="text-gray-300 space-y-2 ml-6">
                <li>Access and review your personal information</li>
                <li>Correct inaccurate or incomplete information</li>
                <li>Delete your account and personal information</li>
                <li>Export your data in a portable format</li>
                <li>Opt out of marketing communications</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">6. Cookies and Tracking</h2>
              <p className="text-gray-300 mb-4">
                We use cookies and similar technologies to enhance your experience:
              </p>
              <ul className="text-gray-300 space-y-2 ml-6">
                <li>Essential cookies for authentication and security</li>
                <li>Analytics cookies to understand usage patterns</li>
                <li>Preference cookies to remember your settings</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">7. Data Retention</h2>
              <p className="text-gray-300 mb-4">
                We retain your information for as long as necessary to provide our services and comply 
                with legal obligations. You can request deletion of your account at any time.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">8. International Transfers</h2>
              <p className="text-gray-300 mb-4">
                Your information may be transferred to and processed in countries other than your own. 
                We ensure appropriate safeguards are in place to protect your information.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">9. Children's Privacy</h2>
              <p className="text-gray-300 mb-4">
                Our service is not intended for children under 13. We do not knowingly collect 
                personal information from children under 13.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">10. Changes to This Policy</h2>
              <p className="text-gray-300 mb-4">
                We may update this privacy policy from time to time. We will notify you of any 
                material changes by posting the new policy on this page and updating the "Last updated" date.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">11. Contact Us</h2>
              <p className="text-gray-300 mb-4">
                If you have any questions about this privacy policy or our data practices, please contact us:
              </p>
              <ul className="text-gray-300 space-y-2 ml-6">
                <li>Email: privacy@priceinsight.com</li>
                <li>Phone: +234 (0) 123 456 7890</li>
                <li>Address: Lagos, Nigeria</li>
              </ul>
            </section>
          </div>

          <div className="mt-12 p-6 bg-gray-800/50 backdrop-blur-md border border-gray-700 rounded-xl">
            <h3 className="text-lg font-semibold text-white mb-2">Questions about your privacy?</h3>
            <p className="text-gray-300 mb-4">
              We're committed to protecting your privacy. If you have any questions or concerns, 
              please don't hesitate to reach out.
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
      <PublicFooter />
    </div>
  );
}