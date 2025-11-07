import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Menu, X } from 'lucide-react';

export function PublicHeader() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <nav className="bg-gray-900/80 backdrop-blur-md border-b border-gray-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center text-xl font-bold text-white">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center mr-2">
                <span className="text-white font-bold text-lg">P</span>
              </div>
              <span className="hidden sm:block">Price Insight</span>
            </Link>
          </div>
          
          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <Link 
              to="/" 
              className="text-gray-300 hover:text-white transition-colors"
            >
              Home
            </Link>
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
              to="/faq" 
              className="text-gray-300 hover:text-white transition-colors"
            >
              FAQ
            </Link>
          </div>
          
          {/* Desktop Auth Buttons */}
          <div className="hidden md:flex items-center space-x-4">
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

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden text-gray-300 hover:text-white transition-colors"
          >
            {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Sidebar */}
      {isMobileMenuOpen && (
        <>
          <div 
            className="fixed inset-0 bg-black/50 z-40 md:hidden"
            onClick={() => setIsMobileMenuOpen(false)}
          />
          <div className={`fixed top-0 right-0 h-screen w-80 bg-gray-900 shadow-2xl z-50 md:hidden transform transition-all duration-500 ease-in-out ${
            isMobileMenuOpen ? 'translate-x-0' : 'translate-x-full'
          }`}>
            <div className="flex items-center justify-between p-6 border-b border-gray-700">
              <div className="flex items-center">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
                  <span className="text-white font-bold text-lg">P</span>
                </div>
                <span className="text-white font-bold text-lg">Price Insight</span>
              </div>
              <button
                onClick={() => setIsMobileMenuOpen(false)}
                className="text-gray-400 hover:text-white transition-colors p-2"
              >
                <X size={20} />
              </button>
            </div>
            <div className="p-6">
              <nav className="space-y-1">
                <Link 
                  to="/" 
                  className="flex items-center px-4 py-3 text-gray-300 hover:text-white hover:bg-gray-800 rounded-lg transition-all duration-200"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Home
                </Link>
                <Link 
                  to="/about" 
                  className="flex items-center px-4 py-3 text-gray-300 hover:text-white hover:bg-gray-800 rounded-lg transition-all duration-200"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  About
                </Link>
                <Link 
                  to="/contact" 
                  className="flex items-center px-4 py-3 text-gray-300 hover:text-white hover:bg-gray-800 rounded-lg transition-all duration-200"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Contact
                </Link>
                <Link 
                  to="/faq" 
                  className="flex items-center px-4 py-3 text-gray-300 hover:text-white hover:bg-gray-800 rounded-lg transition-all duration-200"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  FAQ
                </Link>
              </nav>
              <div className="mt-8 pt-6 border-t border-gray-700 space-y-3">
                <Link 
                  to="/login" 
                  className="block w-full text-center bg-gray-700 text-white px-4 py-3 rounded-lg hover:bg-gray-600 transition-colors font-medium"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Login
                </Link>
                <Link 
                  to="/signup" 
                  className="block w-full text-center bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Sign Up
                </Link>
              </div>
            </div>
          </div>
        </>
      )}
    </nav>
  );
}