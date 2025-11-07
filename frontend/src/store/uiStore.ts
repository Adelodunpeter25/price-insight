import { create } from 'zustand';

interface UIState {
  sidebarOpen: boolean;
  loading: boolean;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
  setLoading: (loading: boolean) => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: false,
  loading: false,
  
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  
  toggleSidebar: () => set((state) => ({ 
    sidebarOpen: !state.sidebarOpen 
  })),
  
  setLoading: (loading) => set({ loading })
}));