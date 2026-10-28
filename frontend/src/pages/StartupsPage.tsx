import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Building2,
  Plus,
  Search,
  Trash2,
  Edit3,
  TrendingUp,
  FileText,
  Sparkles,
  ArrowRight,
  ExternalLink,
} from 'lucide-react';
import { startupApi } from '../api/startups';
import { useApp } from '../components/layout/AppLayout';
import { StartupProfileResponse } from '../types';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Modal } from '../components/ui/Modal';
import { LoadingState } from '../components/feedback/LoadingState';
import { ErrorState } from '../components/feedback/ErrorState';
import { EmptyState } from '../components/feedback/EmptyState';
import { formatDate } from '../utils/formatters';
import { normalizeError } from '../utils/errors';

export const StartupsPage: React.FC = () => {
  const { startups, refreshStartups, setActiveStartupId } = useApp();
  const navigate = useNavigate();

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Delete modal state
  const [startupToDelete, setStartupToDelete] = useState<StartupProfileResponse | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const fetchList = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      await refreshStartups();
    } catch (err) {
      const norm = normalizeError(err);
      setError(norm.message);
    } finally {
      setIsLoading(false);
    }
  }, [refreshStartups]);

  const handleDelete = async () => {
    if (!startupToDelete) return;
    setIsDeleting(true);
    setDeleteError(null);
    try {
      await startupApi.delete(startupToDelete.startup_id);
      await refreshStartups();
      setStartupToDelete(null);
    } catch (err) {
      const norm = normalizeError(err);
      setDeleteError(norm.message);
    } finally {
      setIsDeleting(false);
    }
  };

  const filtered = startups.filter((s) => {
    const term = searchTerm.toLowerCase();
    return (
      s.startup_name.toLowerCase().includes(term) ||
      (s.business_type && s.business_type.toLowerCase().includes(term)) ||
      (s.target_market && s.target_market.toLowerCase().includes(term))
    );
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Top Header */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1rem',
        }}
      >
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>My Startups</h1>
          <p style={{ marginTop: '0.25rem' }}>
            Manage registered venture entities, review profile specifications, and initiate simulations.
          </p>
        </div>

        <Link to="/startups/new">
          <Button variant="primary" leftIcon={<Plus size={16} />}>
            Create Startup
          </Button>
        </Link>
      </div>

      {error && (
        <ErrorState
          title="Could not load startups"
          message={error}
          onRetry={fetchList}
        />
      )}

      {/* Filter / Search Bar */}
      {startups.length > 0 && (
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <div style={{ position: 'relative', flex: 1, maxWidth: '420px' }}>
            <Search
              size={16}
              style={{
                position: 'absolute',
                left: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                color: 'var(--color-text-muted)',
              }}
            />
            <input
              type="text"
              className="form-input"
              placeholder="Search by name, industry, or target market..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{ paddingLeft: '36px' }}
            />
          </div>
        </div>
      )}

      {/* Content Area */}
      {isLoading ? (
        <LoadingState message="Retrieving startup registry..." />
      ) : startups.length === 0 ? (
        <EmptyState
          icon={<Building2 size={28} />}
          title="No Startups Found"
          description="You haven't created any startup profiles yet. Begin by completing the startup creation wizard."
          actionLabel="Create Startup"
          onAction={() => navigate('/startups/new')}
          actionIcon={<Plus size={16} />}
        />
      ) : filtered.length === 0 ? (
        <EmptyState
          title="No matching startups"
          description={`No ventures match your filter term "${searchTerm}".`}
          actionLabel="Clear Filter"
          onAction={() => setSearchTerm('')}
        />
      ) : (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
            gap: '1.5rem',
          }}
        >
          {filtered.map((startup) => (
            <Card
              key={startup.startup_id}
              style={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                height: '100%',
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                  <div>
                    <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>{startup.startup_name}</h3>
                    <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', marginTop: '0.2rem' }}>
                      {startup.business_type || 'Unspecified Type'} • Founded {startup.founded_year || '—'}
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: '0.25rem' }}>
                    <Link to={`/startups/${startup.startup_id}/edit`}>
                      <button
                        className="btn btn-secondary btn-icon"
                        title="Edit Profile"
                        style={{ padding: '0.4rem' }}
                      >
                        <Edit3 size={15} />
                      </button>
                    </Link>
                    <button
                      className="btn btn-secondary btn-icon"
                      title="Delete Startup"
                      style={{ padding: '0.4rem', color: 'var(--color-error-text)' }}
                      onClick={() => setStartupToDelete(startup)}
                    >
                      <Trash2 size={15} />
                    </button>
                  </div>
                </div>

                <p
                  style={{
                    fontSize: '0.875rem',
                    color: 'var(--color-text-secondary)',
                    marginBottom: '1.25rem',
                    display: '-webkit-box',
                    WebkitLineClamp: 3,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                    lineHeight: 1.5,
                  }}
                >
                  {startup.description || 'No detailed business description recorded.'}
                </p>

                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '1fr 1fr',
                    gap: '0.5rem',
                    padding: '0.75rem',
                    backgroundColor: 'var(--color-bg-secondary)',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.78rem',
                    marginBottom: '1.25rem',
                  }}
                >
                  <div>
                    <span style={{ color: 'var(--color-text-muted)', display: 'block' }}>Target Market</span>
                    <strong style={{ color: 'var(--color-text-primary)' }}>
                      {startup.target_market || '—'}
                    </strong>
                  </div>
                  <div>
                    <span style={{ color: 'var(--color-text-muted)', display: 'block' }}>Created On</span>
                    <strong style={{ color: 'var(--color-text-primary)' }}>
                      {formatDate(startup.created_at)}
                    </strong>
                  </div>
                  {startup.website && (
                    <div style={{ gridColumn: 'span 2' }}>
                      <span style={{ color: 'var(--color-text-muted)', display: 'block' }}>Website</span>
                      <a
                        href={startup.website.startsWith('http') ? startup.website : `https://${startup.website}`}
                        target="_blank"
                        rel="noreferrer"
                        style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem', textDecoration: 'underline' }}
                      >
                        <span>{startup.website}</span>
                        <ExternalLink size={12} />
                      </a>
                    </div>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.5rem',
                  borderTop: '1px solid var(--color-border)',
                  paddingTop: '1rem',
                }}
              >
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.5rem' }}>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => {
                      setActiveStartupId(startup.startup_id);
                      navigate(`/startups/${startup.startup_id}/predictions`);
                    }}
                    leftIcon={<TrendingUp size={13} />}
                  >
                    Predict
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => {
                      setActiveStartupId(startup.startup_id);
                      navigate(`/startups/${startup.startup_id}/suggestions`);
                    }}
                    leftIcon={<Sparkles size={13} />}
                  >
                    Advice
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => {
                      setActiveStartupId(startup.startup_id);
                      navigate(`/startups/${startup.startup_id}/reports`);
                    }}
                    leftIcon={<FileText size={13} />}
                  >
                    Reports
                  </Button>
                </div>

                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => {
                    setActiveStartupId(startup.startup_id);
                    navigate(`/startups/${startup.startup_id}`);
                  }}
                  rightIcon={<ArrowRight size={14} />}
                >
                  View Full Profile
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={!!startupToDelete}
        onClose={() => setStartupToDelete(null)}
        title="Delete Startup Profile"
        description="This action is permanent and cannot be undone."
        confirmLabel="Permanently Delete"
        confirmVariant="danger"
        isConfirmLoading={isDeleting}
        onConfirm={handleDelete}
      >
        <p style={{ fontSize: '0.9rem', marginBottom: '1rem' }}>
          Are you sure you want to delete{' '}
          <strong>{startupToDelete?.startup_name}</strong>? All associated financial
          data, team records, locations, predictions, suggestions, and reports will also be deleted.
        </p>
        {deleteError && (
          <div className="alert alert-danger">
            {deleteError}
          </div>
        )}
      </Modal>
    </div>
  );
};
