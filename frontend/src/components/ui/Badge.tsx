import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'neutral' | 'success' | 'warning' | 'danger' | 'risk';
  riskLevel?: 'LOW' | 'MEDIUM' | 'HIGH' | string | null;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  riskLevel,
  className = '',
}) => {
  let badgeClass = 'badge-neutral';

  if (riskLevel) {
    if (riskLevel === 'LOW') badgeClass = 'badge-low-risk';
    else if (riskLevel === 'MEDIUM') badgeClass = 'badge-medium-risk';
    else if (riskLevel === 'HIGH') badgeClass = 'badge-high-risk';
  } else if (variant === 'success') {
    badgeClass = 'badge-success';
  } else if (variant === 'warning') {
    badgeClass = 'badge-warning';
  } else if (variant === 'danger') {
    badgeClass = 'badge-danger';
  }

  return <span className={`badge ${badgeClass} ${className}`}>{children}</span>;
};
