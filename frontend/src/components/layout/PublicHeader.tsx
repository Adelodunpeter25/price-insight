import { Link } from 'react-router-dom';

export function PublicHeader() {
  return (
    <nav className="bg-gray-900/80 backdrop-blur-md border-b border-gray-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center text-xl font-bold text-white">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center mr-2">
                <span className="text-white font-bold text-lg">P</span>
              </div>
              Price Insight
            </Link>
          </div>
          <div className="flex items-center space-x-8">
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
          <div className="flex items-center space-x-4">
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
  );
}