import { useState } from 'react';
import { User, Bell, Settings as SettingsIcon, Save } from 'lucide-react';
import { DashboardLayout } from '../components/layout/DashboardLayout';
import { Card } from '../components/common/Card';
import { Input } from '../components/common/Input';
import { Button } from '../components/common/Button';
import { useAuthContext } from '../context/AuthContext';
import { useToast } from '../hooks/useToast';

export const Settings = () => {
  const { user } = useAuthContext();
  const { success: showSuccess } = useToast();
  const [activeTab, setActiveTab] = useState('account');
  const [isLoading, setIsLoading] = useState(false);

  // Account settings
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [email, setEmail] = useState(user?.email || '');

  // Notification settings
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [frequency, setFrequency] = useState('immediate');
  const [priceDropAlerts, setPriceDropAlerts] = useState(true);
  const [dealAlerts, setDealAlerts] = useState(true);

  // Preferences
  const [priceDropThreshold, setPriceDropThreshold] = useState(10);
  const [priceIncreaseAlerts, setPriceIncreaseAlerts] = useState(false);

  const tabs = [
    { id: 'account', label: 'Account', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'preferences', label: 'Preferences', icon: SettingsIcon },
  ];

  const handleSave = async () => {
    setIsLoading(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      showSuccess('Settings saved successfully');
    } catch (error) {
      console.error('Failed to save settings:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-white">Settings</h1>
          <p className="text-zinc-400 mt-1">Manage your account and preferences</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <Card className="lg:col-span-1">
            <nav className="space-y-2">
              {tabs.map(tab => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      activeTab === tab.id
                        ? 'bg-accent text-white'
                        : 'text-zinc-300 hover:text-white hover:bg-zinc-800/50'
                    }`}
                  >
                    <Icon size={18} />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </nav>
          </Card>

          {/* Content */}
          <div className="lg:col-span-3">
            <Card>
              {activeTab === 'account' && (
                <div className="space-y-6">
                  <h2 className="text-lg font-semibold text-white">Account Information</h2>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Input
                      label="Full Name"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="Enter your full name"
                    />
                    <Input
                      label="Email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="Enter your email"
                    />
                  </div>

                  <div className="pt-4 border-t border-zinc-800">
                    <h3 className="text-md font-medium text-white mb-4">Change Password</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <Input
                        label="Current Password"
                        type="password"
                        placeholder="Enter current password"
                      />
                      <Input
                        label="New Password"
                        type="password"
                        placeholder="Enter new password"
                      />
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'notifications' && (
                <div className="space-y-6">
                  <h2 className="text-lg font-semibold text-white">Notification Settings</h2>
                  
                  <div className="space-y-4">
                    <label className="flex items-center justify-between">
                      <span className="text-white">Email Notifications</span>
                      <input
                        type="checkbox"
                        checked={emailNotifications}
                        onChange={(e) => setEmailNotifications(e.target.checked)}
                        className="rounded"
                      />
                    </label>

                    <div>
                      <label className="block text-sm font-medium text-zinc-300 mb-2">
                        Notification Frequency
                      </label>
                      <select
                        value={frequency}
                        onChange={(e) => setFrequency(e.target.value)}
                        className="w-full px-3 py-2 bg-zinc-900/50 border border-zinc-700/50 rounded-lg text-white"
                      >
                        <option value="immediate">Immediate</option>
                        <option value="daily">Daily Digest</option>
                        <option value="weekly">Weekly Summary</option>
                      </select>
                    </div>

                    <label className="flex items-center justify-between">
                      <span className="text-white">Price Drop Alerts</span>
                      <input
                        type="checkbox"
                        checked={priceDropAlerts}
                        onChange={(e) => setPriceDropAlerts(e.target.checked)}
                        className="rounded"
                      />
                    </label>

                    <label className="flex items-center justify-between">
                      <span className="text-white">Deal Alerts</span>
                      <input
                        type="checkbox"
                        checked={dealAlerts}
                        onChange={(e) => setDealAlerts(e.target.checked)}
                        className="rounded"
                      />
                    </label>
                  </div>
                </div>
              )}

              {activeTab === 'preferences' && (
                <div className="space-y-6">
                  <h2 className="text-lg font-semibold text-white">Preferences</h2>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-zinc-300 mb-2">
                        Price Drop Threshold (%)
                      </label>
                      <input
                        type="range"
                        min="1"
                        max="50"
                        value={priceDropThreshold}
                        onChange={(e) => setPriceDropThreshold(Number(e.target.value))}
                        className="w-full"
                      />
                      <div className="flex justify-between text-xs text-zinc-400 mt-1">
                        <span>1%</span>
                        <span className="text-accent">{priceDropThreshold}%</span>
                        <span>50%</span>
                      </div>
                    </div>

                    <label className="flex items-center justify-between">
                      <span className="text-white">Price Increase Alerts</span>
                      <input
                        type="checkbox"
                        checked={priceIncreaseAlerts}
                        onChange={(e) => setPriceIncreaseAlerts(e.target.checked)}
                        className="rounded"
                      />
                    </label>
                  </div>
                </div>
              )}

              {/* Save Button */}
              <div className="pt-6 border-t border-zinc-800">
                <Button
                  variant="primary"
                  loading={isLoading}
                  onClick={handleSave}
                >
                  <Save size={16} className="mr-2" />
                  Save Changes
                </Button>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};