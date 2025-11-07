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
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSidebarOpen(false)}
            className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm lg:hidden"
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.aside
        initial={{ x: -280 }}
        animate={{ x: sidebarOpen ? 0 : -280 }}
        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
        className={`
          fixed top-0 left-0 z-50 h-full w-64 glass-card border-r border-zinc-800/50
          lg:translate-x-0 lg:static lg:z-auto
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        <div className="flex items-center justify-between p-4 lg:hidden">
          <span className="text-white font-semibold text-lg">Menu</span>
          <button
            onClick={() => setSidebarOpen(false)}
            className="text-zinc-400 hover:text-white transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <nav className="px-4 py-6 space-y-2">
          {navigation.map((item, index) => (
            <motion.div
              key={item.name}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <NavLink
                to={item.href}
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-accent text-white'
                      : 'text-zinc-300 hover:text-white hover:bg-zinc-800/50'
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
            </motion.div>
          ))}
        </nav>
      </motion.aside>
    </>
  );
};