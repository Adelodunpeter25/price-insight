import { Menu, Bell, Sun, Moon, User } from 'lucide-react';
import { motion } from 'framer-motion';
import { useTheme } from '../../context/ThemeContext';
import { useAuthContext } from '../../context/AuthContext';
import { useUIStore } from '../../store/uiStore';
import { useAlerts } from '../../hooks/useAlerts';
import { Badge } from './Badge';

export const Navbar = () => {
  const { theme, toggleTheme } = useTheme();
  const { user, logout } = useAuthContext();
  const { toggleSidebar } = useUIStore();
  const { unreadCount } = useAlerts();

  return (
    <motion.nav
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="sticky top-0 z-40 bg-gray-900/80 backdrop-blur-md border-b border-gray-800 px-4 py-3"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={toggleSidebar}
            className="p-2 text-gray-400 hover:text-white transition-colors lg:hidden"
          >
            <Menu size={20} />
          </button>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={toggleTheme}
            className="p-2 text-gray-400 hover:text-white transition-colors"
          >
            {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
          </button>

          <div className="relative">
            <button className="p-2 text-gray-400 hover:text-white transition-colors">
              <Bell size={20} />
            </button>
            {unreadCount > 0 && (
              <Badge 
                variant="danger" 
                size="sm" 
                className="absolute -top-1 -right-1 min-w-[20px] h-5 flex items-center justify-center"
              >
                {unreadCount}
              </Badge>
            )}
          </div>

          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center">
              <User size={16} className="text-gray-300" />
            </div>
            <span className="text-gray-300 text-sm hidden sm:block">
              {user?.full_name || user?.email}
            </span>
          </div>
        </div>
      </div>
    </motion.nav>
  );
};