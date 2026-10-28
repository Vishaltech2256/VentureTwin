import React, { useState, useEffect, useCallback, createContext, useContext } from 'react';
import { Outlet, useParams, useNavigate } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { startupApi } from '../../api/startups';
import { StartupProfileResponse } from '../../types';

interface AppContextType {
  startups: StartupProfileResponse[];
  activeStartupId: number | null;
  setActiveStartupId: (id: number) => void;
  refreshStartups: () => Promise<void>;
  isLoadingStartups: boolean;
}

const defaultAppContext: AppContextType = {
  startups: [],
  activeStartupId: null,
  setActiveStartupId: () => {},
  refreshStartups: async () => {},
  isLoadingStartups: false,
};

const AppContext = createContext<AppContextType>(defaultAppContext);

export const useApp = (): AppContextType => {
  const ctx = useContext(AppContext);
  return ctx || defaultAppContext;
};

export const AppLayout: React.FC = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [startups, setStartups] = useState<StartupProfileResponse[]>([]);
  const [activeStartupId, setActiveStartupId] = useState<number | null>(null);
  const [isLoadingStartups, setIsLoadingStartups] = useState(true);

  const { startupId } = useParams<{ startupId?: string }>();
  const navigate = useNavigate();

  const fetchStartups = useCallback(async () => {
    try {
      const data = await startupApi.list();
      setStartups(data);
      if (data.length > 0) {
        if (startupId) {
          const parsed = Number(startupId);
          setActiveStartupId(parsed);
        } else {
          setActiveStartupId((prev) => prev ?? data[0].startup_id);
        }
      } else {
        setActiveStartupId(null);
      }
    } catch {
      // Handled quietly in layout
    } finally {
      setIsLoadingStartups(false);
    }
  }, [startupId]);

  useEffect(() => {
    fetchStartups();
  }, [fetchStartups]);

  // Synchronize URL param with activeStartupId if URL changes
  useEffect(() => {
    if (startupId) {
      const numId = Number(startupId);
      if (!isNaN(numId)) {
        setActiveStartupId(numId);
      }
    }
  }, [startupId]);

  const handleSelectStartup = useCallback((id: number) => {
    setActiveStartupId(id);
    const currentPath = window.location.pathname;
    if (currentPath.includes('/startups/')) {
      const parts = currentPath.split('/');
      if (parts.length >= 4) {
        navigate(`/startups/${id}/${parts[3]}`);
      } else {
        navigate(`/startups/${id}`);
      }
    }
  }, [navigate]);

  return (
    <AppContext.Provider
      value={{
        startups,
        activeStartupId,
        setActiveStartupId: handleSelectStartup,
        refreshStartups: fetchStartups,
        isLoadingStartups,
      }}
    >
      <div className="app-container">
        <Sidebar
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
          activeStartupId={activeStartupId}
        />

        <div className="main-content">
          <Header
            onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
            startups={startups}
            activeStartupId={activeStartupId}
            onSelectStartup={handleSelectStartup}
          />

          <main className="page-wrapper animate-fade-in">
            <Outlet />
          </main>
        </div>
      </div>
    </AppContext.Provider>
  );
};
