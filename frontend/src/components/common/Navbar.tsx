import { useState } from 'react';
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
  const { alerts, unreadCount } = useAlerts();
  const [showNotifications, setShowNotifications] = useState(false);

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
            <button 
              onClick={() => setShowNotifications(!showNotifications)}
              className="p-2 text-gray-400 hover:text-white transition-colors"
            >
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
            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 bg-gray-800 rounded-lg shadow-lg border border-gray-700 py-2 max-h-96 overflow-y-auto">
                <div className="px-4 py-2 border-b border-gray-700">
                  <h3 className="text-white font-semibold">Notifications</h3>
                </div>
                {alerts.length === 0 ? (
                  <div className="px-4 py-6 text-center text-gray-400">
                    No notifications
                  </div>
                ) : (
                  alerts.slice(0, 5).map((alert) => (
                    <div key={alert.id} className="px-4 py-3 hover:bg-gray-700 border-b border-gray-700 last:border-b-0">
                      <p className="text-white text-sm">{alert.message}</p>
                      <p className="text-gray-400 text-xs mt-1">
                        {new Date(alert.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  ))
                )}
                {alerts.length > 0 && (
                  <div className="px-4 py-2 border-t border-gray-700">
                    <button 
                      onClick={() => setShowNotifications(false)}
                      className="text-blue-400 hover:text-blue-300 text-sm"
                    >
                      View all alerts
                    </button>
                  </div>
                )}
              </div>
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