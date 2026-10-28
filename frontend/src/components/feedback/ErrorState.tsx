import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from '../ui/Button';

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  isRetrying?: boolean;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Failed to load content',
  message = 'An unexpected error occurred while communicating with the backend.',
  onRetry,
  isRetrying = false,
}) => {
  return (
    <div
      className="vt-card"
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '3rem 2rem',
        textAlign: 'center',
        borderStyle: 'dashed',
      }}
    >
      <div
        style={{
          width: 44,
          height: 44,
          borderRadius: '50%',
          backgroundColor: 'var(--color-error-bg)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--color-error-text)',
          marginBottom: '1rem',
        }}
      >
        <AlertCircle size={22} />
      </div>
      <h3 style={{ fontSize: '1.15rem', marginBottom: '0.35rem' }}>{title}</h3>
      <p style={{ maxWidth: '440px', marginBottom: '1.5rem', fontSize: '0.9rem' }}>{message}</p>
      {onRetry && (
        <Button
          variant="secondary"
          size="sm"
          onClick={onRetry}
          isLoading={isRetrying}
          leftIcon={<RefreshCw size={14} />}
        >
          Retry Request
        </Button>
      )}
    </div>
  );
};
