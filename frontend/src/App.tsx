import { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { Toaster } from 'react-hot-toast';
import { ProtectedRoute, Spinner, ErrorBoundary } from './components';
import ScrollToTop from './components/ScrollToTop';

// Public pages
import { Home, About, Contact, FAQ, Privacy, Terms } from './pages/public';
import { Login, Signup, ForgotPassword } from './pages/auth';
import { NotFound } from './pages';

// Lazy load protected pages
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Products = lazy(() => import('./pages/Products'));
const ProductDetail = lazy(() => import('./pages/ProductDetail'));
const Deals = lazy(() => import('./pages/Deals'));
const Alerts = lazy(() => import('./pages/Alerts'));
const Settings = lazy(() => import('./pages/Settings'));

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <AuthProvider>
          <Router>
            <ScrollToTop />
            <div className="min-h-screen bg-gray-900">
              <Routes>
                {/* Public Routes */}
                <Route path="/" element={<Home />} />
                <Route path="/about" element={<About />} />
                <Route path="/contact" element={<Contact />} />
                <Route path="/faq" element={<FAQ />} />
                <Route path="/privacy" element={<Privacy />} />
                <Route path="/terms" element={<Terms />} />
                
                {/* Auth Routes */}
                <Route path="/login" element={<Login />} />
                <Route path="/signup" element={<Signup />} />
                <Route path="/forgot-password" element={<ForgotPassword />} />
                
                {/* Protected Routes */}
                <Route path="/dashboard" element={
                  <ProtectedRoute>
                    <Suspense fallback={<div className="min-h-screen bg-gray-900 flex items-center justify-center"><Spinner size="lg" /></div>}>
                      <Dashboard />
                    </Suspense>
                  </ProtectedRoute>
                } />
                
                <Route path="/products" element={
                  <ProtectedRoute>
                    <Suspense fallback={<div className="min-h-screen bg-gray-900 flex items-center justify-center"><Spinner size="lg" /></div>}>
                      <Products />
                    </Suspense>
                  </ProtectedRoute>
                } />
                
                <Route path="/products/:id" element={
                  <ProtectedRoute>
                    <Suspense fallback={<div className="min-h-screen bg-gray-900 flex items-center justify-center"><Spinner size="lg" /></div>}>
                      <ProductDetail />
                    </Suspense>
                  </ProtectedRoute>
                } />
                
                <Route path="/deals" element={
                  <ProtectedRoute>
                    <Suspense fallback={<div className="min-h-screen bg-gray-900 flex items-center justify-center"><Spinner size="lg" /></div>}>
                      <Deals />
                    </Suspense>
                  </ProtectedRoute>
                } />
                
                <Route path="/alerts" element={
                  <ProtectedRoute>
                    <Suspense fallback={<div className="min-h-screen bg-gray-900 flex items-center justify-center"><Spinner size="lg" /></div>}>
                      <Alerts />
                    </Suspense>
                  </ProtectedRoute>
                } />
                
                <Route path="/settings" element={
                  <ProtectedRoute>
                    <Suspense fallback={<div className="min-h-screen bg-gray-900 flex items-center justify-center"><Spinner size="lg" /></div>}>
                      <Settings />
                    </Suspense>
                  </ProtectedRoute>
                } />
                
                {/* Redirect /app to /dashboard */}
                <Route path="/app" element={<Navigate to="/dashboard" replace />} />
                
                {/* 404 Route */}
                <Route path="*" element={<NotFound />} />
              </Routes>
              
              {/* Toast notifications */}
              <Toaster
                position="top-right"
                toastOptions={{
                  duration: 4000,
                  style: {
                    background: '#1f2937',
                    color: '#f3f4f6',
                    border: '1px solid #374151',
                  },
                  success: {
                    iconTheme: {
                      primary: '#10b981',
                      secondary: '#f3f4f6',
                    },
                  },
                  error: {
                    iconTheme: {
                      primary: '#ef4444',
                      secondary: '#f3f4f6',
                    },
                  },
                }}
              />
            </div>
          </Router>
        </AuthProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
