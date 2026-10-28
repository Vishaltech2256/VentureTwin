import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Building2,
  TrendingUp,
  FileText,
  Sparkles,
  Plus,
  ArrowRight,
  RefreshCw,
  MapPin,
  Users,
  Compass,
} from 'lucide-react';
import { dashboardApi } from '../api/dashboard';
import { startupApi } from '../api/startups';
import { useAuth } from '../context/AuthContext';
import { useApp } from '../components/layout/AppLayout';
import {
  DashboardResponse,
  StartupFullData,
} from '../types';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { LoadingState } from '../components/feedback/LoadingState';
import { ErrorState } from '../components/feedback/ErrorState';
import { EmptyState } from '../components/feedback/EmptyState';
import { formatINR, formatPercent, formatDate } from '../utils/formatters';
import { normalizeError } from '../utils/errors';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const { startups, activeStartupId, setActiveStartupId, isLoadingStartups } = useApp();
  const navigate = useNavigate();

  const memberName = user?.full_name?.trim() || (user?.email ? user.email.split('@')[0] : 'Member');

  const [dashboardData, setDashboardData] = useState<DashboardResponse | null>(null);
  const [activeStartupData, setActiveStartupData] = useState<StartupFullData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingActive, setIsLoadingActive] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardStats = useCallback(async () => {
    setError(null);
    try {
      const data = await dashboardApi.get();
      setDashboardData(data);
    } catch (err) {
      const norm = normalizeError(err);
      setError(norm.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchActiveStartupData = useCallback(async (id: number) => {
    setIsLoadingActive(true);
    try {
      const full = await startupApi.getFull(id);
      setActiveStartupData(full);
    } catch {
      setActiveStartupData(null);
    } finally {
      setIsLoadingActive(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardStats();
  }, [fetchDashboardStats]);

  useEffect(() => {
    if (activeStartupId) {
      fetchActiveStartupData(activeStartupId);
    } else {
      setActiveStartupData(null);
    }
  }, [activeStartupId, fetchActiveStartupData]);

  if (isLoading || isLoadingStartups) {
    return <LoadingState message="Loading dashboard telemetry..." />;
  }

  if (error) {
    return (
      <ErrorState
        title="Dashboard Error"
        message={error}
        onRetry={fetchDashboardStats}
      />
    );
  }

  const hasStartups = (dashboardData?.total_startups ?? 0) > 0 || startups.length > 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Top Welcome & Quick Actions */}
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
          <div
            style={{
              fontSize: '0.95rem',
              fontWeight: 600,
              color: 'var(--color-text-secondary)',
              marginBottom: '0.35rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
            }}
          >
            <span>Hi, <strong style={{ color: 'var(--color-text-primary)', fontWeight: 700 }}>{memberName}</strong></span>
            <span>👋</span>
          </div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Platform Overview</h1>
          <p style={{ marginTop: '0.25rem' }}>
            System telemetry and live digital twin performance across registered ventures.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => {
              fetchDashboardStats();
              if (activeStartupId) fetchActiveStartupData(activeStartupId);
            }}
            leftIcon={<RefreshCw size={14} />}
          >
            Refresh
          </Button>
          <Link to="/startups/new">
            <Button variant="primary" size="sm" leftIcon={<Plus size={16} />}>
              Create Startup
            </Button>
          </Link>
        </div>
      </div>

      {/* Aggregate Metrics Header Cards */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '1.25rem',
        }}
      >
        <Card
          className="interactive-stat-card metric-stat-card"
          onClick={() => navigate('/startups')}
          role="button"
          tabIndex={0}
          aria-label="Total Startups - click to view all startups"
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              navigate('/startups');
            }
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-text-secondary)' }}>
              Total Startups
            </span>
            <div
              className="metric-corner-btn"
              aria-hidden="true"
            >
              <Building2 size={16} />
            </div>
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#111111' }}>
            {dashboardData?.total_startups ?? 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>
            Active entity profiles
          </div>
        </Card>

        <Card
          className="interactive-stat-card metric-stat-card"
          onClick={() => navigate(activeStartupId ? `/startups/${activeStartupId}/predictions` : '/predictions')}
          role="button"
          tabIndex={0}
          aria-label="Prediction Runs - click to view prediction runs"
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              navigate(activeStartupId ? `/startups/${activeStartupId}/predictions` : '/predictions');
            }
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-text-secondary)' }}>
              Prediction Runs
            </span>
            <div
              className="metric-corner-btn"
              aria-hidden="true"
            >
              <TrendingUp size={16} />
            </div>
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#111111' }}>
            {dashboardData?.total_predictions ?? 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>
            Telemetry evaluations executed
          </div>
        </Card>

        <Card
          className="interactive-stat-card metric-stat-card"
          onClick={() => navigate(activeStartupId ? `/startups/${activeStartupId}/reports` : '/reports')}
          role="button"
          tabIndex={0}
          aria-label="Executive Reports - click to view executive reports"
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              navigate(activeStartupId ? `/startups/${activeStartupId}/reports` : '/reports');
            }
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-text-secondary)' }}>
              Executive Reports
            </span>
            <div
              className="metric-corner-btn"
              aria-hidden="true"
            >
              <FileText size={16} />
            </div>
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#111111' }}>
            {dashboardData?.total_reports ?? 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>
            Compiled ReportLab PDFs
          </div>
        </Card>
      </div>

      {!hasStartups ? (
        <EmptyState
          icon={<Building2 size={24} />}
          title="No Startups Registered Yet"
          description="Create your first startup profile to unlock predictive simulation models, financial risk tracking, and executive report generation."
          actionLabel="Create Startup Profile"
          onAction={() => navigate('/startups/new')}
          actionIcon={<Plus size={16} />}
        />
      ) : (
        <>
          {/* Active Startup Deep Dive Panel */}
          {activeStartupId && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: '1rem',
                  borderBottom: '1px solid var(--color-border)',
                  paddingBottom: '0.75rem',
                }}
              >
                <div>
                  <h2 style={{ fontSize: '1.35rem', fontWeight: 700 }}>
                    Active Venture: {activeStartupData?.profile?.startup_name || 'Loading...'}
                  </h2>
                  <p style={{ fontSize: '0.85rem' }}>
                    {activeStartupData?.profile?.business_type || 'Startup'} • Founded{' '}
                    {activeStartupData?.profile?.founded_year || '—'}
                  </p>
                </div>

                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <Link to={`/startups/${activeStartupId}`}>
                    <Button variant="secondary" size="sm" rightIcon={<ArrowRight size={14} />}>
                      View Profile
                    </Button>
                  </Link>
                  <Link to={`/startups/${activeStartupId}/predictions`}>
                    <Button variant="primary" size="sm" rightIcon={<TrendingUp size={14} />}>
                      Run Prediction
                    </Button>
                  </Link>
                </div>
              </div>

              {isLoadingActive ? (
                <LoadingState message="Loading startup telemetry..." />
              ) : activeStartupData ? (
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
                    gap: '1.25rem',
                    alignItems: 'stretch',
                  }}
                >
                  {/* Card 1: Latest Prediction Summary Card */}
                  <Card
                    className="interactive-stat-card"
                    title="Prediction Intelligence"
                    action={
                      activeStartupData.latestPrediction ? (
                        <Badge riskLevel={activeStartupData.latestPrediction.risk_level}>
                          {activeStartupData.latestPrediction.risk_level} Risk
                        </Badge>
                      ) : (
                        <Badge variant="neutral">No Run</Badge>
                      )
                    }
                    style={{ display: 'flex', flexDirection: 'column', height: '100%' }}
                  >
                    {activeStartupData.latestPrediction ? (
                      <div style={{ display: 'flex', flexDirection: 'column', flex: 1, justifyContent: 'space-between', gap: '1rem' }}>
                        {/* Hero Highlight Banner */}
                        <div
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            padding: '1rem 1.25rem',
                            backgroundColor: 'var(--color-bg-secondary)',
                            borderRadius: 'var(--radius-sm)',
                            border: '1px solid var(--color-border)',
                          }}
                        >
                          <div>
                            <div style={{ fontSize: '2.25rem', fontWeight: 800, lineHeight: 1.1 }}>
                              {formatPercent(activeStartupData.latestPrediction.success_probability)}
                            </div>
                            <div style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', fontWeight: 600, marginTop: '0.25rem' }}>
                              Calculated Success Probability
                            </div>
                          </div>
                          <div
                            style={{
                              padding: '6px 10px',
                              backgroundColor: 'rgba(34, 197, 94, 0.1)',
                              borderRadius: '6px',
                              border: '1px solid rgba(34, 197, 94, 0.25)',
                              fontSize: '0.72rem',
                              fontWeight: 700,
                              color: '#16A34A',
                              letterSpacing: '0.04em',
                            }}
                          >
                            AI SIMULATED
                          </div>
                        </div>

                        {/* 2x2 Clean Metric Grid */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                          <div style={{ padding: '0.65rem 0.85rem', backgroundColor: 'var(--color-bg-secondary)', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
                            <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.72rem', textTransform: 'uppercase', fontWeight: 600 }}>
                              Projected Revenue
                            </span>
                            <span style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--color-text-primary)' }}>
                              {formatINR(activeStartupData.latestPrediction.predicted_annual_revenue)}
                            </span>
                          </div>

                          <div style={{ padding: '0.65rem 0.85rem', backgroundColor: 'var(--color-bg-secondary)', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
                            <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.72rem', textTransform: 'uppercase', fontWeight: 600 }}>
                              Projected Profit
                            </span>
                            <span style={{ fontWeight: 700, fontSize: '0.95rem', color: (activeStartupData.latestPrediction.predicted_annual_profit ?? 0) >= 0 ? '#16A34A' : '#DC2626' }}>
                              {formatINR(activeStartupData.latestPrediction.predicted_annual_profit)}
                            </span>
                          </div>

                          <div style={{ padding: '0.65rem 0.85rem', backgroundColor: 'var(--color-bg-secondary)', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
                            <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.72rem', textTransform: 'uppercase', fontWeight: 600 }}>
                              Est. Break-Even
                            </span>
                            <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>
                              {activeStartupData.latestPrediction.break_even_months
                                ? `${activeStartupData.latestPrediction.break_even_months} Months`
                                : 'Indeterminate'}
                            </span>
                          </div>

                          <div style={{ padding: '0.65rem 0.85rem', backgroundColor: 'var(--color-bg-secondary)', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
                            <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.72rem', textTransform: 'uppercase', fontWeight: 600 }}>
                              Evaluation Date
                            </span>
                            <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>
                              {formatDate(activeStartupData.latestPrediction.created_at)}
                            </span>
                          </div>
                        </div>

                        {/* Bottom Summary Strip */}
                        <div
                          style={{
                            padding: '0.65rem 0.85rem',
                            borderRadius: '6px',
                            border: '1px solid var(--color-border)',
                            backgroundColor: 'rgba(0,0,0,0.02)',
                            fontSize: '0.8rem',
                            color: 'var(--color-text-secondary)',
                            lineHeight: 1.45,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical',
                          }}
                        >
                          {activeStartupData.latestPrediction.prediction_summary}
                        </div>
                      </div>
                    ) : (
                      <div style={{ textAlign: 'center', padding: '1.5rem 1rem' }}>
                        <p style={{ fontSize: '0.875rem', marginBottom: '1rem' }}>
                          No prediction has been executed for this startup yet.
                        </p>
                        <Link to={`/startups/${activeStartupId}/predictions`}>
                          <Button size="sm" variant="primary">
                            Run Initial Prediction
                          </Button>
                        </Link>
                      </div>
                    )}
                  </Card>

                  {/* Card 2: Financial Telemetry Card */}
                  <Card
                    className="interactive-stat-card"
                    title="Financial Profile"
                    action={<Badge variant="neutral">Capital Telemetry</Badge>}
                    style={{ display: 'flex', flexDirection: 'column', height: '100%' }}
                  >
                    {activeStartupData.financial ? (
                      <div style={{ display: 'flex', flexDirection: 'column', flex: 1, justifyContent: 'space-between', gap: '1rem' }}>
                        {/* Hero Highlight Banner matching Card 1 */}
                        <div
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            padding: '1rem 1.25rem',
                            backgroundColor: 'var(--color-bg-secondary)',
                            borderRadius: 'var(--radius-sm)',
                            border: '1px solid var(--color-border)',
                          }}
                        >
                          <div>
                            <div style={{ fontSize: '2.25rem', fontWeight: 800, lineHeight: 1.1 }}>
                              {formatINR(Number(activeStartupData.financial.initial_investment || 0) + Number(activeStartupData.financial.funding_raised || 0))}
                            </div>
                            <div style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', fontWeight: 600, marginTop: '0.25rem' }}>
                              Total Capital Injected
                            </div>
                          </div>
                          <div style={{ textAlign: 'right' }}>
                            <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                              Ext. Funding
                            </div>
                            <div style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--color-text-primary)' }}>
                              {formatINR(activeStartupData.financial.funding_raised)}
                            </div>
                          </div>
                        </div>

                        {/* 2x2 Clean Metric Grid */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                          <div style={{ padding: '0.65rem 0.85rem', backgroundColor: 'var(--color-bg-secondary)', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
                            <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.72rem', textTransform: 'uppercase', fontWeight: 600 }}>
                              Monthly Revenue
                            </span>
                            <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>
                              {formatINR(activeStartupData.financial.monthly_revenue)}
                            </span>
                          </div>

                          <div style={{ padding: '0.65rem 0.85rem', backgroundColor: 'var(--color-bg-secondary)', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
                            <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.72rem', textTransform: 'uppercase', fontWeight: 600 }}>
                              Monthly Expenses
                            </span>
                            <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>
                              {formatINR(activeStartupData.financial.monthly_expenses)}
                            </span>
                          </div>

                          <div style={{ padding: '0.65rem 0.85rem', backgroundColor: 'var(--color-bg-secondary)', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
                            <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.72rem', textTransform: 'uppercase', fontWeight: 600 }}>
                              Annual Revenue
                            </span>
                            <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>
                              {formatINR(activeStartupData.financial.annual_revenue)}
                            </span>
                          </div>

                          <div style={{ padding: '0.65rem 0.85rem', backgroundColor: 'var(--color-bg-secondary)', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
                            <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.72rem', textTransform: 'uppercase', fontWeight: 600 }}>
                              Monthly Burn Rate
                            </span>
                            <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>
                              {formatINR(activeStartupData.financial.burn_rate)}
                            </span>
                          </div>
                        </div>

                        {/* Bottom Summary Strip matching Card 1 */}
                        <div
                          style={{
                            padding: '0.65rem 0.85rem',
                            borderRadius: '6px',
                            border: '1px solid var(--color-border)',
                            backgroundColor: 'rgba(0,0,0,0.02)',
                            fontSize: '0.8rem',
                            color: 'var(--color-text-secondary)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                          }}
                        >
                          <span>
                            Initial Investment:{' '}
                            <strong style={{ color: 'var(--color-text-primary)' }}>
                              {formatINR(activeStartupData.financial.initial_investment)}
                            </strong>
                          </span>
                          <span style={{ color: '#16A34A', fontWeight: 600 }}>● Active Runway</span>
                        </div>
                      </div>
                    ) : (
                      <div style={{ textAlign: 'center', padding: '1.5rem 1rem' }}>
                        <p style={{ fontSize: '0.875rem', marginBottom: '1rem' }}>
                          Financial telemetry has not yet been submitted.
                        </p>
                        <Link to={`/startups/${activeStartupId}/edit`}>
                          <Button size="sm" variant="secondary">
                            Add Financial Data
                          </Button>
                        </Link>
                      </div>
                    )}
                  </Card>

                  {/* Card 3: Team & Operation Card */}
                  <Card
                    className="interactive-stat-card"
                    title="Team & Operational Footprint"
                    action={<Badge variant="neutral">Verified Entity</Badge>}
                    style={{ display: 'flex', flexDirection: 'column', height: '100%' }}
                  >
                    <div style={{ display: 'flex', flexDirection: 'column', flex: 1, justifyContent: 'space-between', gap: '1rem' }}>
                      {/* Hero Highlight Banner matching Card 1 & 2 */}
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: '1rem 1.25rem',
                          backgroundColor: 'var(--color-bg-secondary)',
                          borderRadius: 'var(--radius-sm)',
                          border: '1px solid var(--color-border)',
                        }}
                      >
                        <div>
                          <div style={{ fontSize: '2.25rem', fontWeight: 800, lineHeight: 1.1 }}>
                            {activeStartupData.team?.employee_count ?? 1}
                          </div>
                          <div style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', fontWeight: 600, marginTop: '0.25rem' }}>
                            Total Team Employees
                          </div>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                          <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                            Co-Founder
                          </div>
                          <div style={{ fontSize: '0.85rem', fontWeight: 700, color: activeStartupData.team?.has_technical_cofounder ? '#16A34A' : 'var(--color-text-secondary)' }}>
                            {activeStartupData.team?.has_technical_cofounder ? 'Tech Present' : 'Single Founder'}
                          </div>
                        </div>
                      </div>

                      {/* 2x2 Clean Metric Grid matching Card 1 & 2 */}
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                        <div style={{ padding: '0.65rem 0.85rem', backgroundColor: 'var(--color-bg-secondary)', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', marginBottom: '0.2rem' }}>
                            <Users size={13} style={{ color: 'var(--color-text-muted)' }} />
                            <span style={{ color: 'var(--color-text-muted)', fontSize: '0.72rem', textTransform: 'uppercase', fontWeight: 600 }}>
                              Founder
                            </span>
                          </div>
                          <div style={{ fontWeight: 700, fontSize: '0.92rem', color: 'var(--color-text-primary)' }}>
                            {activeStartupData.team?.founder_name || 'Founder'}
                          </div>
                          <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>
                            {activeStartupData.team?.founder_experience_years !== null && activeStartupData.team?.founder_experience_years !== undefined
                              ? `${activeStartupData.team.founder_experience_years} yrs exp`
                              : 'Exp not set'}
                          </div>
                        </div>

                        <div style={{ padding: '0.65rem 0.85rem', backgroundColor: 'var(--color-bg-secondary)', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', marginBottom: '0.2rem' }}>
                            <Building2 size={13} style={{ color: 'var(--color-text-muted)' }} />
                            <span style={{ color: 'var(--color-text-muted)', fontSize: '0.72rem', textTransform: 'uppercase', fontWeight: 600 }}>
                              Business Type
                            </span>
                          </div>
                          <div style={{ fontWeight: 700, fontSize: '0.92rem', color: 'var(--color-text-primary)' }}>
                            {activeStartupData.profile?.business_type || 'Startup'}
                          </div>
                          <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>
                            Founded {activeStartupData.profile?.founded_year || '—'}
                          </div>
                        </div>

                        <div style={{ padding: '0.65rem 0.85rem', backgroundColor: 'var(--color-bg-secondary)', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', marginBottom: '0.2rem' }}>
                            <MapPin size={13} style={{ color: 'var(--color-text-muted)' }} />
                            <span style={{ color: 'var(--color-text-muted)', fontSize: '0.72rem', textTransform: 'uppercase', fontWeight: 600 }}>
                              Location
                            </span>
                          </div>
                          <div style={{ fontWeight: 700, fontSize: '0.92rem', color: 'var(--color-text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {[activeStartupData.location?.city, activeStartupData.location?.state].filter(Boolean).join(', ') || 'Not specified'}
                          </div>
                          <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>
                            {activeStartupData.location?.country || 'India'}
                          </div>
                        </div>

                        <div style={{ padding: '0.65rem 0.85rem', backgroundColor: 'var(--color-bg-secondary)', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', marginBottom: '0.2rem' }}>
                            <Compass size={13} style={{ color: 'var(--color-text-muted)' }} />
                            <span style={{ color: 'var(--color-text-muted)', fontSize: '0.72rem', textTransform: 'uppercase', fontWeight: 600 }}>
                              Premises
                            </span>
                          </div>
                          <div style={{ fontWeight: 700, fontSize: '0.92rem', color: 'var(--color-text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {activeStartupData.land?.has_land ? `${activeStartupData.land.land_area_sqft} sqft` : 'Remote / Virtual'}
                          </div>
                          <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>
                            {activeStartupData.land?.has_land ? (activeStartupData.land.land_status || 'Owned') : 'No physical plot'}
                          </div>
                        </div>
                      </div>

                      {/* Bottom Summary Strip matching Card 1 & 2 */}
                      <div
                        style={{
                          padding: '0.65rem 0.85rem',
                          borderRadius: '6px',
                          border: '1px solid var(--color-border)',
                          backgroundColor: 'rgba(0,0,0,0.02)',
                          fontSize: '0.8rem',
                          color: 'var(--color-text-secondary)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                        }}
                      >
                        <span>Operational HQ</span>
                        <span style={{ color: 'var(--color-text-primary)', fontWeight: 600 }}>
                          {[activeStartupData.location?.city, activeStartupData.location?.country].filter(Boolean).join(', ') || 'Headquarters'}
                        </span>
                      </div>
                    </div>
                  </Card>

                  {/* AI Recommendations Quick Feed */}
                  <Card
                    title="Active Recommendations"
                    action={
                      <Link to={`/startups/${activeStartupId}/suggestions`}>
                        <Button variant="secondary" size="sm">
                          View All ({activeStartupData.suggestions.length})
                        </Button>
                      </Link>
                    }
                  >
                    {activeStartupData.suggestions.length > 0 ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                        {activeStartupData.suggestions.slice(0, 3).map((sugg) => (
                          <div
                            key={sugg.suggestion_id}
                            style={{
                              padding: '0.75rem',
                              borderRadius: 'var(--radius-sm)',
                              border: '1px solid var(--color-border)',
                              backgroundColor: 'var(--color-bg-secondary)',
                            }}
                          >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                              <span style={{ fontWeight: 700, fontSize: '0.85rem' }}>{sugg.title}</span>
                              <Badge
                                variant={
                                  sugg.priority === 'HIGH'
                                    ? 'danger'
                                    : sugg.priority === 'MEDIUM'
                                    ? 'warning'
                                    : 'neutral'
                                }
                              >
                                {sugg.priority}
                              </Badge>
                            </div>
                            <p style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', lineClamp: 2 }}>
                              {sugg.description}
                            </p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div style={{ textAlign: 'center', padding: '1.5rem 1rem' }}>
                        <Sparkles size={24} style={{ color: 'var(--color-text-muted)', marginBottom: '0.5rem' }} />
                        <p style={{ fontSize: '0.85rem' }}>
                          No AI suggestions currently available for this venture.
                        </p>
                        <Link to={`/startups/${activeStartupId}/suggestions`} style={{ marginTop: '0.75rem', display: 'inline-block' }}>
                          <Button size="sm" variant="primary">
                            Generate Recommendations
                          </Button>
                        </Link>
                      </div>
                    )}
                  </Card>
                </div>
              ) : null}
            </div>
          )}

          {/* Recent Startups Table */}
          {dashboardData?.recent_startups && dashboardData.recent_startups.length > 0 && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Recent Startups</h3>
                <Link to="/startups" style={{ fontSize: '0.85rem', fontWeight: 600, textDecoration: 'underline' }}>
                  View All Startups
                </Link>
              </div>

              <div className="vt-table-container">
                <table className="vt-table">
                  <thead>
                    <tr>
                      <th>Startup Name</th>
                      <th>Business Type</th>
                      <th>Target Market</th>
                      <th>Created</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dashboardData.recent_startups.map((st) => (
                      <tr key={st.startup_id}>
                        <td style={{ fontWeight: 600 }}>{st.startup_name}</td>
                        <td>{st.business_type || '—'}</td>
                        <td>{st.target_market || '—'}</td>
                        <td>{formatDate(st.created_at)}</td>
                        <td>
                          <div style={{ display: 'flex', gap: '0.5rem' }}>
                            <Button
                              variant="secondary"
                              size="sm"
                              onClick={() => {
                                setActiveStartupId(st.startup_id);
                                navigate(`/startups/${st.startup_id}`);
                              }}
                            >
                              Details
                            </Button>
                            <Button
                              variant="primary"
                              size="sm"
                              onClick={() => {
                                setActiveStartupId(st.startup_id);
                                navigate(`/startups/${st.startup_id}/predictions`);
                              }}
                            >
                              Predict
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
