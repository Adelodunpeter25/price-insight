import { NavLink } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  LayoutDashboard, 
  Package, 
  Tag, 
  Bell, 
  Settings,
  X
} from 'lucide-react';
import { useUIStore } from '../../store/uiStore';
import { Badge } from './Badge';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Products', href: '/products', icon: Package, badge: '12' },
  { name: 'Deals', href: '/deals', icon: Tag, badge: '5' },
  { name: 'Alerts', href: '/alerts', icon: Bell, badge: '3' },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export const Sidebar = () => {
  const { sidebarOpen, setSidebarOpen } = useUIStore();

  return (
    <>
      {/* Mobile overlay */}
      <div 
        className={`fixed inset-0 bg-black/50 z-40 lg:hidden transition-opacity duration-300 ${
          sidebarOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
        }`}
        onClick={() => setSidebarOpen(false)}
      />

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 z-50 h-screen w-64 bg-gray-900 shadow-2xl lg:static lg:z-auto transform transition-transform duration-300 ease-in-out ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        <div className="flex items-center justify-between p-6 border-b border-gray-700 lg:hidden">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
              <span className="text-white font-bold text-lg">P</span>
            </div>
            <span className="text-white font-bold text-lg">Price Insight</span>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="text-gray-400 hover:text-white transition-colors p-2"
          >
            <X size={20} />
          </button>
        </div>

        <nav className="p-6">
          <div className="space-y-1">
            {navigation.map((item, index) => (
              <NavLink
                key={item.name}
                to={item.href}
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) =>
                  `flex items-center justify-between px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-300 hover:text-white hover:bg-gray-800'
                  }`
                }
              >
                <div className="flex items-center space-x-3">
                  <item.icon size={18} />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <Badge variant="info" size="sm">
                    {item.badge}
                  </Badge>
                )}
              </NavLink>
            ))}
          </div>
        </nav>
      </aside>
    </>
  );
};