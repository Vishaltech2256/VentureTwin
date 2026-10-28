import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  TrendingUp,
  Play,
  AlertCircle,
  Clock,
  Sparkles,
  FileText,
  Building2,
  CheckCircle2,
  ArrowLeft,
  ChevronRight,
} from 'lucide-react';
import { predictionApi } from '../api/predictions';
import { startupApi } from '../api/startups';
import { useApp } from '../components/layout/AppLayout';
import { PredictionResponse, StartupProfileResponse } from '../types';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { LoadingState } from '../components/feedback/LoadingState';
import { ErrorState } from '../components/feedback/ErrorState';
import { EmptyState } from '../components/feedback/EmptyState';
import { formatINR, formatPercent, formatDate, formatDateTime, parseAssumptions } from '../utils/formatters';
import { normalizeError } from '../utils/errors';

export const PredictionsPage: React.FC = () => {
  const { startupId } = useParams<{ startupId: string }>();
  const { startups, activeStartupId, setActiveStartupId } = useApp();

  const effectiveId = startupId
    ? Number(startupId)
    : (activeStartupId ?? (startups.length > 0 ? startups[0].startup_id : null));

  const [currentStartup, setCurrentStartup] = useState<StartupProfileResponse | null>(null);
  const [predictions, setPredictions] = useState<PredictionResponse[]>([]);
  const [latestPrediction, setLatestPrediction] = useState<PredictionResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [runSuccess, setRunSuccess] = useState(false);

  const loadData = useCallback(async () => {
    if (!effectiveId) {
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const [profile, predsList] = await Promise.all([
        startupApi.get(effectiveId),
        predictionApi.list(effectiveId),
      ]);
      setCurrentStartup(profile);
      setPredictions(predsList);
      if (predsList.length > 0) {
        setLatestPrediction(predsList[0]);
      } else {
        setLatestPrediction(null);
      }
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

  const handleRunPrediction = async () => {
    if (!effectiveId) return;
    setIsRunning(true);
    setError(null);
    setRunSuccess(false);
    try {
      const result = await predictionApi.run(effectiveId);
      setLatestPrediction(result);
      setPredictions((prev) => [result, ...prev]);
      setRunSuccess(true);
      setTimeout(() => setRunSuccess(false), 4000);
    } catch (err) {
      const norm = normalizeError(err);
      setError(norm.message);
    } finally {
      setIsRunning(false);
    }
  };

  if (!effectiveId) {
    return (
      <EmptyState
        icon={<Building2 size={28} />}
        title="No Startup Selected"
        description="Choose a startup from the registry or create a new profile to execute digital twin prediction engine runs."
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
    return <LoadingState message="Loading prediction evaluations..." />;
  }

  const assumptionsList = parseAssumptions(latestPrediction?.assumptions);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Top Header */}
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
            <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Prediction Engine</h1>
            <p style={{ marginTop: '0.25rem' }}>
              Venture: <strong>{currentStartup?.startup_name}</strong> • Deterministic rule-based success modeling.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <Link to={`/startups/${effectiveId}/suggestions`}>
              <Button variant="secondary" size="sm" leftIcon={<Sparkles size={14} />}>
                AI Suggestions
              </Button>
            </Link>
            <Button
              variant="primary"
              onClick={handleRunPrediction}
              isLoading={isRunning}
              leftIcon={<Play size={15} />}
            >
              Run New Prediction
            </Button>
          </div>
        </div>
      </div>

      {runSuccess && (
        <div className="alert alert-success animate-fade-in" role="alert">
          <CheckCircle2 size={18} style={{ flexShrink: 0, marginTop: 2 }} />
          <div>New prediction simulation calculated and persisted successfully!</div>
        </div>
      )}

      {error && (
        <div className="alert alert-danger" role="alert">
          <AlertCircle size={18} style={{ flexShrink: 0, marginTop: 2 }} />
          <div>{error}</div>
        </div>
      )}

      {/* Main Latest Result View */}
      {latestPrediction ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Hero Score Banner */}
          <div
            className="vt-card"
            style={{
              padding: '2rem',
              backgroundColor: '#FFFFFF',
              border: '1px solid var(--color-border)',
            }}
          >
            <div
              style={{
                display: 'flex',
                flexWrap: 'wrap',
                justifyContent: 'space-between',
                alignItems: 'center',
                gap: '1.5rem',
                borderBottom: '1px solid var(--color-border)',
                paddingBottom: '1.5rem',
                marginBottom: '1.5rem',
              }}
            >
              <div>
                <span
                  style={{
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    color: 'var(--color-text-muted)',
                    letterSpacing: '0.05em',
                  }}
                >
                  Latest Prediction Evaluation
                </span>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '1rem', marginTop: '0.25rem' }}>
                  <span style={{ fontSize: '3.25rem', fontWeight: 800, letterSpacing: '-0.04em' }}>
                    {formatPercent(latestPrediction.success_probability)}
                  </span>
                  <div>
                    <span style={{ fontSize: '1rem', fontWeight: 700 }}>Success Probability</span>
                    <div style={{ marginTop: '0.2rem' }}>
                      <Badge riskLevel={latestPrediction.risk_level}>
                        {latestPrediction.risk_level} Risk Level
                      </Badge>
                    </div>
                  </div>
                </div>
              </div>

              <div style={{ textAlign: 'right', fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', justifyContent: 'flex-end' }}>
                  <Clock size={14} />
                  <span>Computed: {formatDateTime(latestPrediction.created_at)}</span>
                </div>
                <div style={{ marginTop: '0.25rem' }}>
                  Run ID #{latestPrediction.prediction_id}
                </div>
              </div>
            </div>

            {/* Financial Projections Row */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '1.25rem',
                marginBottom: '1.5rem',
              }}
            >
              <div
                style={{
                  padding: '1rem',
                  backgroundColor: 'var(--color-bg-secondary)',
                  borderRadius: 'var(--radius-sm)',
                }}
              >
                <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                  Projected Annual Revenue
                </span>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, marginTop: '0.25rem' }}>
                  {formatINR(latestPrediction.predicted_annual_revenue)}
                </div>
                <span style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>
                  Annualized (12 months + growth)
                </span>
              </div>

              <div
                style={{
                  padding: '1rem',
                  backgroundColor: 'var(--color-bg-secondary)',
                  borderRadius: 'var(--radius-sm)',
                }}
              >
                <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                  Projected Annual Profit
                </span>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, marginTop: '0.25rem' }}>
                  {formatINR(latestPrediction.predicted_annual_profit)}
                </div>
                <span style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>
                  Revenue minus projected expenses
                </span>
              </div>

              <div
                style={{
                  padding: '1rem',
                  backgroundColor: 'var(--color-bg-secondary)',
                  borderRadius: 'var(--radius-sm)',
                }}
              >
                <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                  Estimated Break-Even
                </span>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, marginTop: '0.25rem' }}>
                  {latestPrediction.break_even_months
                    ? `${latestPrediction.break_even_months} Months`
                    : 'Indeterminate'}
                </div>
                <span style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>
                  Capital recovery timeline
                </span>
              </div>
            </div>

            {/* Prediction Summary text */}
            <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: '1.25rem' }}>
              <h4 style={{ fontSize: '0.95rem', marginBottom: '0.5rem' }}>Evaluation Summary</h4>
              <p style={{ fontSize: '0.9rem', lineHeight: 1.6, color: 'var(--color-text-primary)' }}>
                {latestPrediction.prediction_summary}
              </p>
            </div>
          </div>

          {/* Model Assumptions Breakdown */}
          {assumptionsList.length > 0 && (
            <Card title="Scoring Factors & Telemetry Assumptions">
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {assumptionsList.map((assumption, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '0.75rem',
                      padding: '0.65rem 0.85rem',
                      backgroundColor: 'var(--color-bg-secondary)',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: '0.85rem',
                    }}
                  >
                    <CheckCircle2
                      size={16}
                      style={{ color: '#111111', flexShrink: 0, marginTop: '2px' }}
                    />
                    <span>{assumption}</span>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Historical Run Log */}
          {predictions.length > 1 && (
            <div>
              <h3 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>Simulation History</h3>
              <div className="vt-table-container">
                <table className="vt-table">
                  <thead>
                    <tr>
                      <th>Run ID</th>
                      <th>Timestamp</th>
                      <th>Success Probability</th>
                      <th>Risk Level</th>
                      <th>Annual Revenue</th>
                      <th>Annual Profit</th>
                      <th>Break-Even</th>
                    </tr>
                  </thead>
                  <tbody>
                    {predictions.map((p) => (
                      <tr
                        key={p.prediction_id}
                        style={{
                          backgroundColor:
                            p.prediction_id === latestPrediction.prediction_id
                              ? 'var(--color-bg-subtle)'
                              : 'inherit',
                        }}
                      >
                        <td style={{ fontWeight: 600 }}>#{p.prediction_id}</td>
                        <td>{formatDateTime(p.created_at)}</td>
                        <td style={{ fontWeight: 700 }}>{formatPercent(p.success_probability)}</td>
                        <td>
                          <Badge riskLevel={p.risk_level}>{p.risk_level}</Badge>
                        </td>
                        <td>{formatINR(p.predicted_annual_revenue)}</td>
                        <td>{formatINR(p.predicted_annual_profit)}</td>
                        <td>
                          {p.break_even_months ? `${p.break_even_months} Mo` : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      ) : (
        <EmptyState
          icon={<TrendingUp size={28} />}
          title="No Predictions Executed Yet"
          description="Click 'Run New Prediction' to execute the rule-based simulation engine on your startup's financial and operational data."
          actionLabel="Run Initial Prediction"
          onAction={handleRunPrediction}
          actionIcon={<Play size={16} />}
        />
      )}
    </div>
  );
};
