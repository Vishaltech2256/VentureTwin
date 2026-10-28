import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Building,
  PlusCircle,
  TrendingUp,
  Sparkles,
  FileText,
  UserCheck,
  X,
  Layers,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  activeStartupId?: number | null;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose, activeStartupId }) => {
  const { user } = useAuth();
  const location = useLocation();
  const pathname = location.pathname;

  const isTopicActive = (id: string) => {
    if (id === 'dashboard') return pathname === '/dashboard';
    if (id === 'startups') {
      return (
        pathname === '/startups' ||
        (pathname.startsWith('/startups/') &&
          !pathname.includes('/predictions') &&
          !pathname.includes('/suggestions') &&
          !pathname.includes('/reports') &&
          pathname !== '/startups/new')
      );
    }
    if (id === 'new') return pathname === '/startups/new';
    if (id === 'predictions') return pathname.includes('/predictions');
    if (id === 'suggestions') return pathname.includes('/suggestions');
    if (id === 'reports') return pathname.includes('/reports');
    if (id === 'account') return pathname === '/account';
    return false;
  };

  interface NavItem {
    id: string;
    to: string;
    label: string;
    icon: React.ReactNode;
    badge?: string;
  }

  const navLinks: NavItem[] = [
    {
      id: 'dashboard',
      to: '/dashboard',
      label: 'Dashboard',
      icon: <LayoutDashboard size={18} />,
    },
    {
      id: 'startups',
      to: '/startups',
      label: 'My Startups',
      icon: <Building size={18} />,
    },
    {
      id: 'new',
      to: '/startups/new',
      label: 'Create Startup',
      icon: <PlusCircle size={18} />,
    },
    {
      id: 'predictions',
      to: activeStartupId ? `/startups/${activeStartupId}/predictions` : '/predictions',
      label: 'Predictions',
      icon: <TrendingUp size={18} />,
    },
    {
      id: 'suggestions',
      to: activeStartupId ? `/startups/${activeStartupId}/suggestions` : '/suggestions',
      label: 'AI Suggestions',
      icon: <Sparkles size={18} />,
    },
    {
      id: 'reports',
      to: activeStartupId ? `/startups/${activeStartupId}/reports` : '/reports',
      label: 'Reports',
      icon: <FileText size={18} />,
    },
    {
      id: 'account',
      to: '/account',
      label: 'Account',
      icon: <UserCheck size={18} />,
    },
  ];

  return (
    <>
      {isOpen && <div className="sidebar-backdrop" onClick={onClose} />}

      <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div className="brand-logo">
            <div
              style={{
                width: 28,
                height: 28,
                backgroundColor: '#ffffff',
                color: '#000000',
                borderRadius: 'var(--radius-xs)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Layers size={16} />
            </div>
            <span>VentureTwin</span>
            <span className="brand-badge">AI</span>
          </div>

          <button
            className="btn btn-secondary btn-icon mobile-nav-toggle"
            onClick={onClose}
            aria-label="Close menu"
          >
            <X size={16} />
          </button>
        </div>

        <nav className="sidebar-nav">
          <div
            style={{
              padding: '0.25rem 0.5rem 0.5rem',
              fontSize: '0.72rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              color: '#666666',
              letterSpacing: '0.06em',
            }}
          >
            Platform
          </div>

          {navLinks.map((item) => {
            const active = isTopicActive(item.id);

            return (
              <Link
                key={item.id}
                to={item.to}
                onClick={onClose}
                className={`nav-item ${active ? 'active' : ''}`}
              >
                {item.icon}
                <span style={{ flex: 1 }}>{item.label}</span>
                {item.badge && (
                  <span
                    style={{
                      fontSize: '0.65rem',
                      padding: '1px 5px',
                      borderRadius: 'var(--radius-xs)',
                      backgroundColor: active ? '#000000' : '#222222',
                      color: active ? '#ffffff' : '#888888',
                      border: active ? '1px solid #000000' : '1px solid #333333',
                    }}
                  >
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <div className="user-snippet">
            <div className="user-avatar">
              {(user?.full_name || user?.email || 'U').charAt(0).toUpperCase()}
            </div>
            <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              <div className="user-name">
                {user?.full_name || 'Founder'}
              </div>
              <div className="user-email">
                {user?.email}
              </div>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
