import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Sparkles,
  RefreshCw,
  Trash2,
  TrendingUp,
  AlertCircle,
  Building2,
  Filter,
  CheckCircle2,
  ArrowLeft,
  Calendar,
} from 'lucide-react';
import { aiSuggestionApi } from '../api/suggestions';
import { startupApi } from '../api/startups';
import { useApp } from '../components/layout/AppLayout';
import { AISuggestionResponse, StartupProfileResponse } from '../types';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { LoadingState } from '../components/feedback/LoadingState';
import { ErrorState } from '../components/feedback/ErrorState';
import { EmptyState } from '../components/feedback/EmptyState';
import { formatDate } from '../utils/formatters';
import { normalizeError } from '../utils/errors';

export const SuggestionsPage: React.FC = () => {
  const { startupId } = useParams<{ startupId: string }>();
  const { startups, activeStartupId, setActiveStartupId } = useApp();

  const effectiveId = startupId
    ? Number(startupId)
    : (activeStartupId ?? (startups.length > 0 ? startups[0].startup_id : null));

  const [currentStartup, setCurrentStartup] = useState<StartupProfileResponse | null>(null);
  const [suggestions, setSuggestions] = useState<AISuggestionResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [genSuccess, setGenSuccess] = useState<string | null>(null);

  // Detail Modal
  const [selectedSuggestion, setSelectedSuggestion] = useState<AISuggestionResponse | null>(null);

  // Delete State
  const [toDelete, setToDelete] = useState<AISuggestionResponse | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Category filter
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');

  const loadData = useCallback(async () => {
    if (!effectiveId) {
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const [profile, list] = await Promise.all([
        startupApi.get(effectiveId),
        aiSuggestionApi.list(effectiveId),
      ]);
      setCurrentStartup(profile);
      setSuggestions(list);
    } catch (err) {
      const norm = normalizeError(err);
      setError(norm.message);
    } finally {
      setIsLoading(false);
    }
  }, [effectiveId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleGenerate = async () => {
    if (!effectiveId) return;
    setIsGenerating(true);
    setError(null);
    setGenSuccess(null);
    try {
      const res = await aiSuggestionApi.generate(effectiveId);
      setSuggestions(res.suggestions);
      setGenSuccess(`Generated ${res.generated_count} strategic recommendations.`);
      setTimeout(() => setGenSuccess(null), 4000);
    } catch (err) {
      const norm = normalizeError(err);
      if (norm.status === 400) {
        setError('No prediction is available for this startup. Please run a prediction first before generating suggestions.');
      } else {
        setError(norm.message);
      }
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDelete = async () => {
    if (!toDelete) return;
    setIsDeleting(true);
    try {
      await aiSuggestionApi.delete(toDelete.suggestion_id);
      setSuggestions((prev) => prev.filter((s) => s.suggestion_id !== toDelete.suggestion_id));
      setToDelete(null);
    } catch (err) {
      const norm = normalizeError(err);
      setError(norm.message);
    } finally {
      setIsDeleting(false);
    }
  };

  const categories = ['ALL', ...Array.from(new Set(suggestions.map((s) => s.category)))];

  const filtered = suggestions.filter(
    (s) => selectedCategory === 'ALL' || s.category === selectedCategory
  );

  if (!effectiveId) {
    return (
      <EmptyState
        icon={<Building2 size={28} />}
        title="No Startup Selected"
        description="Choose a startup from the registry or create a new profile to inspect and generate recommendations."
        action={
          <Link to={startups.length > 0 ? '/startups' : '/startups/new'}>
            <Button variant="primary">
              {startups.length > 0 ? 'Select from Registry' : 'Create Startup Profile'}
            </Button>
          </Link>
        }
      />
    );
  }

  if (isLoading) {
    return <LoadingState message="Loading AI recommendations..." />;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Header */}
      <div>
        <Link
          to={`/startups/${effectiveId}`}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.4rem',
            fontSize: '0.85rem',
            color: 'var(--color-text-secondary)',
            fontWeight: 500,
            marginBottom: '0.75rem',
          }}
        >
          <ArrowLeft size={14} />
          <span>Back to {currentStartup?.startup_name || 'Startup'}</span>
        </Link>

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
            <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>AI Recommendations</h1>
            <p style={{ marginTop: '0.25rem' }}>
              Venture: <strong>{currentStartup?.startup_name}</strong> • Context-aware strategic advice.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <Link to={`/startups/${effectiveId}/predictions`}>
              <Button variant="secondary" size="sm" leftIcon={<TrendingUp size={14} />}>
                View Predictions
              </Button>
            </Link>
            <Button
              variant="primary"
              onClick={handleGenerate}
              isLoading={isGenerating}
              leftIcon={<Sparkles size={15} />}
            >
              Generate Suggestions
            </Button>
          </div>
        </div>
      </div>

      {genSuccess && (
        <div className="alert alert-success animate-fade-in" role="alert">
          <CheckCircle2 size={18} style={{ flexShrink: 0, marginTop: 2 }} />
          <div>{genSuccess}</div>
        </div>
      )}

      {error && (
        <div className="alert alert-danger" role="alert">
          <AlertCircle size={18} style={{ flexShrink: 0, marginTop: 2 }} />
          <div style={{ flex: 1 }}>{error}</div>
          {error.includes('run a prediction first') && (
            <Link to={`/startups/${effectiveId}/predictions`}>
              <Button size="sm" variant="primary">
                Run Prediction
              </Button>
            </Link>
          )}
        </div>
      )}

      {/* Category Filter Pills */}
      {suggestions.length > 0 && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#666666', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Category:
          </span>
          <div
            style={{
              display: 'inline-flex',
              backgroundColor: '#0c0c0c',
              padding: '4px',
              borderRadius: '8px',
              border: '1px solid #1f1f1f',
              gap: '4px',
              flexWrap: 'wrap',
            }}
          >
            {categories.map((cat) => {
              const isActive = selectedCategory === cat;
              return (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  style={{
                    backgroundColor: isActive ? '#ffffff' : 'transparent',
                    color: isActive ? '#000000' : '#888888',
                    border: 'none',
                    borderRadius: '6px',
                    fontWeight: isActive ? 700 : 500,
                    fontSize: '0.78rem',
                    padding: '0.4rem 0.85rem',
                    cursor: 'pointer',
                    transition: 'all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1)',
                    boxShadow: isActive ? '0 2px 6px rgba(0, 0, 0, 0.3)' : 'none',
                  }}
                >
                  {cat}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Suggestions List */}
      {suggestions.length === 0 ? (
        <EmptyState
          icon={<Sparkles size={28} />}
          title="No AI Recommendations Generated"
          description="Click 'Generate Suggestions' to evaluate your startup's latest prediction and create contextual operational and financial advice."
          actionLabel="Generate Suggestions Now"
          onAction={handleGenerate}
          actionIcon={<Sparkles size={16} />}
        />
      ) : filtered.length === 0 ? (
        <EmptyState
          title="No suggestions in this category"
          description={`No recommendations match category "${selectedCategory}".`}
          actionLabel="Reset Category"
          onAction={() => setSelectedCategory('ALL')}
        />
      ) : (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))',
            gap: '1.25rem',
          }}
        >
          {filtered.map((sugg) => (
            <Card
              key={sugg.suggestion_id}
              style={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                height: '100%',
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    <Badge
                      variant={
                        sugg.priority === 'HIGH'
                          ? 'danger'
                          : sugg.priority === 'MEDIUM'
                          ? 'warning'
                          : 'neutral'
                      }
                    >
                      {sugg.priority} Priority
                    </Badge>
                    <span
                      style={{
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        color: 'var(--color-text-secondary)',
                        backgroundColor: 'var(--color-bg-secondary)',
                        padding: '2px 8px',
                        borderRadius: 'var(--radius-xs)',
                        border: '1px solid var(--color-border)',
                      }}
                    >
                      {sugg.category}
                    </span>
                  </div>

                  <button
                    className="btn btn-secondary btn-icon"
                    title="Delete Suggestion"
                    style={{ padding: '0.35rem', color: 'var(--color-error-text)' }}
                    onClick={() => setToDelete(sugg)}
                  >
                    <Trash2 size={14} />
                  </button>
                </div>

                <h3 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '0.5rem' }}>
                  {sugg.title}
                </h3>

                <p style={{ fontSize: '0.875rem', lineHeight: 1.6, color: 'var(--color-text-secondary)', marginBottom: '1rem' }}>
                  {sugg.description}
                </p>
              </div>

              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  borderTop: '1px solid var(--color-border)',
                  paddingTop: '0.75rem',
                  fontSize: '0.78rem',
                  color: 'var(--color-text-muted)',
                }}
              >
                <span>ID #{sugg.suggestion_id}</span>
                <span>{formatDate(sugg.created_at)}</span>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={!!toDelete}
        onClose={() => setToDelete(null)}
        title="Delete AI Suggestion"
        description="Permanently remove this recommendation."
        confirmLabel="Delete"
        confirmVariant="danger"
        isConfirmLoading={isDeleting}
        onConfirm={handleDelete}
      >
        <p style={{ fontSize: '0.9rem' }}>
          Are you sure you want to delete recommendation "{toDelete?.title}"?
        </p>
      </Modal>
    </div>
  );
};
