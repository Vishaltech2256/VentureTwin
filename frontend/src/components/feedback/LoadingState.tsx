import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
  subtext?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Loading data...',
  subtext,
}) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '3rem 1.5rem',
        textAlign: 'center',
      }}
    >
      <Loader2
        size={32}
        className="animate-spin"
        style={{ color: 'var(--color-text-primary)', marginBottom: '1rem' }}
      />
      <h4 style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>{message}</h4>
      {subtext && <p style={{ fontSize: '0.85rem', marginTop: '0.25rem' }}>{subtext}</p>}
    </div>
  );
};
