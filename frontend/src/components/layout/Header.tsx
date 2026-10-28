import React from 'react';
import { Menu, Building2 } from 'lucide-react';
import { StartupProfileResponse } from '../../types';

interface HeaderProps {
  onToggleSidebar: () => void;
  startups?: StartupProfileResponse[];
  activeStartupId?: number | null;
  onSelectStartup?: (id: number) => void;
}

export const Header: React.FC<HeaderProps> = ({
  onToggleSidebar,
  startups = [],
  activeStartupId,
  onSelectStartup,
}) => {
  const handleStartupChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selected = Number(e.target.value);
    if (selected && onSelectStartup) {
      onSelectStartup(selected);
    }
  };

  return (
    <header className="top-header">
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <button
          className="btn btn-secondary btn-icon mobile-nav-toggle"
          onClick={onToggleSidebar}
          aria-label="Toggle Navigation Menu"
        >
          <Menu size={18} />
        </button>

        {startups.length > 0 && onSelectStartup && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Building2 size={16} style={{ color: 'var(--color-text-secondary)' }} />
            <select
              className="form-select no-arrow-select"
              value={activeStartupId || ''}
              onChange={handleStartupChange}
              style={{
                width: 'auto',
                minWidth: '100px',
                padding: '0.4rem 0.85rem',
                fontSize: '0.85rem',
                fontWeight: 600,
                appearance: 'none',
                WebkitAppearance: 'none',
                MozAppearance: 'none',
                backgroundImage: 'none',
                cursor: 'pointer',
                textAlign: 'left',
              }}
              aria-label="Active Startup Selector"
            >
              {startups.map((s) => (
                <option key={s.startup_id} value={s.startup_id}>
                  {s.startup_name}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>
    </header>
  );
};
