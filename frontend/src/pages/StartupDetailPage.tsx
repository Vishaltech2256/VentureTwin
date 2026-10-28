import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  Building2,
  DollarSign,
  Users,
  MapPin,
  Compass,
  Edit3,
  Trash2,
  TrendingUp,
  Sparkles,
  FileText,
  ExternalLink,
  ArrowLeft,
  Calendar,
} from 'lucide-react';
import { startupApi } from '../api/startups';
import { StartupFullData } from '../types';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { LoadingState } from '../components/feedback/LoadingState';
import { ErrorState } from '../components/feedback/ErrorState';
import { formatINR, formatPercent, formatDate, formatDateTime } from '../utils/formatters';
import { normalizeError } from '../utils/errors';
import { useApp } from '../components/layout/AppLayout';

export const StartupDetailPage: React.FC = () => {
  const { startupId } = useParams<{ startupId: string }>();
  const navigate = useNavigate();
  const { refreshStartups, setActiveStartupId } = useApp();

  const [data, setData] = useState<StartupFullData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const [activeTab, setActiveTab] = useState<'overview' | 'financials' | 'team' | 'location' | 'land'>('overview');

  const fetchStartupData = useCallback(async () => {
    if (!startupId || isNaN(Number(startupId))) {
      setError('Invalid or missing startup ID.');
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const full = await startupApi.getFull(Number(startupId));
      setData(full);
    } catch (err) {
      const norm = normalizeError(err);
      setError(norm.message);
    } finally {
      setIsLoading(false);
    }
  }, [startupId]);

  useEffect(() => {
    fetchStartupData();
  }, [fetchStartupData]);

  const handleDelete = async () => {
    if (!startupId) return;
    setIsDeleting(true);
    setDeleteError(null);
    try {
      await startupApi.delete(Number(startupId));
      await refreshStartups();
      navigate('/startups');
    } catch (err) {
      const norm = normalizeError(err);
      setDeleteError(norm.message);
    } finally {
      setIsDeleting(false);
    }
  };

  if (isLoading) {
    return <LoadingState message="Loading startup telemetry profile..." />;
  }

  if (error || !data) {
    return (
      <ErrorState
        title="Startup Not Found"
        message={error || 'Could not find the requested startup.'}
        onRetry={fetchStartupData}
      />
    );
  }

  const { profile, financial, team, location, land, latestPrediction, suggestions, reports } = data;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Back button & Breadcrumb */}
      <div>
        <Link
          to="/startups"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.4rem',
            fontSize: '0.85rem',
            color: 'var(--color-text-secondary)',
            fontWeight: 500,
            marginBottom: '1rem',
          }}
        >
          <ArrowLeft size={14} />
          <span>Back to My Startups</span>
        </Link>

        {/* Profile Header Block */}
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            gap: '1.5rem',
            paddingBottom: '1.5rem',
            borderBottom: '1px solid var(--color-border)',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.25rem' }}>
              <h1 style={{ fontSize: '2rem', fontWeight: 800 }}>{profile.startup_name}</h1>
              {latestPrediction && (
                <Badge riskLevel={latestPrediction.risk_level}>
                  {latestPrediction.risk_level} Risk
                </Badge>
              )}
            </div>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', fontSize: '0.85rem', color: 'var(--color-text-secondary)' }}>
              <span>{profile.business_type || 'Unspecified Type'}</span>
              <span>•</span>
              <span>Target: {profile.target_market || 'Unspecified'}</span>
              <span>•</span>
              <span>Founded: {profile.founded_year || '—'}</span>
              <span>•</span>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
                <Calendar size={13} /> Registered {formatDate(profile.created_at)}
              </span>
            </div>

            {profile.website && (
              <div style={{ marginTop: '0.5rem' }}>
                <a
                  href={profile.website.startsWith('http') ? profile.website : `https://${profile.website}`}
                  target="_blank"
                  rel="noreferrer"
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.35rem',
                    fontSize: '0.85rem',
                    color: '#111111',
                    textDecoration: 'underline',
                  }}
                >
                  <span>{profile.website}</span>
                  <ExternalLink size={12} />
                </a>
              </div>
            )}
          </div>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            <Link to={`/startups/${startupId}/predictions`}>
              <Button variant="primary" size="sm" leftIcon={<TrendingUp size={14} />}>
                Predictions
              </Button>
            </Link>
            <Link to={`/startups/${startupId}/suggestions`}>
              <Button variant="secondary" size="sm" leftIcon={<Sparkles size={14} />}>
                Suggestions ({suggestions.length})
              </Button>
            </Link>
            <Link to={`/startups/${startupId}/reports`}>
              <Button variant="secondary" size="sm" leftIcon={<FileText size={14} />}>
                Reports ({reports.length})
              </Button>
            </Link>
            <Link to={`/startups/${startupId}/edit`}>
              <Button variant="secondary" size="sm" leftIcon={<Edit3 size={14} />}>
                Edit
              </Button>
            </Link>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setIsDeleteModalOpen(true)}
              style={{ color: 'var(--color-error-text)' }}
            >
              <Trash2 size={14} />
            </Button>
          </div>
        </div>
      </div>

      {/* Topics / Tabs Pill Bar */}
      <div
        style={{
          display: 'inline-flex',
          backgroundColor: '#0c0c0c',
          padding: '5px',
          borderRadius: '10px',
          border: '1px solid #1f1f1f',
          gap: '4px',
          overflowX: 'auto',
          maxWidth: '100%',
        }}
      >
        {[
          { key: 'overview', label: 'Overview', icon: <Building2 size={15} /> },
          { key: 'financials', label: 'Financial Telemetry', icon: <DollarSign size={15} /> },
          { key: 'team', label: 'Team', icon: <Users size={15} /> },
          { key: 'location', label: 'Location', icon: <MapPin size={15} /> },
          { key: 'land', label: 'Land & Premises', icon: <Compass size={15} /> },
        ].map((tab) => {
          const isActive = activeTab === tab.key;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.6rem 1.1rem',
                backgroundColor: isActive ? '#ffffff' : '#141414',
                color: isActive ? '#000000' : '#888888',
                border: isActive ? '1px solid #ffffff' : '1px solid #222222',
                borderRadius: '7px',
                fontWeight: isActive ? 700 : 500,
                cursor: 'pointer',
                fontSize: '0.875rem',
                whiteSpace: 'nowrap',
                transition: 'all 0.25s cubic-bezier(0.2, 0.8, 0.2, 1)',
                boxShadow: isActive ? '0 2px 8px rgba(0, 0, 0, 0.3)' : 'none',
              }}
            >
              {tab.icon}
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Panels */}
      {activeTab === 'overview' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
          <Card title="Description & Market Position">
            <p style={{ fontSize: '0.95rem', lineHeight: 1.6, color: 'var(--color-text-primary)' }}>
              {profile.description || 'No business description provided yet.'}
            </p>

            <div style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid var(--color-border)' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '0.85rem' }}>
                <div>
                  <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.75rem' }}>Business Type</span>
                  <strong>{profile.business_type || '—'}</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.75rem' }}>Target Market</span>
                  <strong>{profile.target_market || '—'}</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.75rem' }}>Founded</span>
                  <strong>{profile.founded_year || '—'}</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.75rem' }}>Last Updated</span>
                  <strong>{formatDateTime(profile.updated_at)}</strong>
                </div>
              </div>
            </div>
          </Card>

          <Card
            title="Latest Simulation Result"
            action={
              <Link to={`/startups/${startupId}/predictions`}>
                <Button variant="secondary" size="sm">
                  Full History
                </Button>
              </Link>
            }
          >
            {latestPrediction ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'baseline',
                    gap: '0.75rem',
                    padding: '1rem',
                    backgroundColor: 'var(--color-bg-secondary)',
                    borderRadius: 'var(--radius-sm)',
                  }}
                >
                  <div style={{ fontSize: '2.5rem', fontWeight: 800 }}>
                    {formatPercent(latestPrediction.success_probability)}
                  </div>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>Success Probability</div>
                    <Badge riskLevel={latestPrediction.risk_level}>{latestPrediction.risk_level} Risk</Badge>
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '0.85rem' }}>
                  <div>
                    <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.75rem' }}>
                      Projected Annual Revenue
                    </span>
                    <strong>{formatINR(latestPrediction.predicted_annual_revenue)}</strong>
                  </div>
                  <div>
                    <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.75rem' }}>
                      Projected Annual Profit
                    </span>
                    <strong>{formatINR(latestPrediction.predicted_annual_profit)}</strong>
                  </div>
                  <div>
                    <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.75rem' }}>
                      Break-Even Horizon
                    </span>
                    <strong>
                      {latestPrediction.break_even_months
                        ? `${latestPrediction.break_even_months} Months`
                        : 'Indeterminate'}
                    </strong>
                  </div>
                  <div>
                    <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.75rem' }}>
                      Prediction Date
                    </span>
                    <strong>{formatDate(latestPrediction.created_at)}</strong>
                  </div>
                </div>

                <p style={{ fontSize: '0.825rem', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
                  {latestPrediction.prediction_summary}
                </p>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '2rem 1rem' }}>
                <TrendingUp size={28} style={{ color: 'var(--color-text-muted)', marginBottom: '0.5rem' }} />
                <p style={{ fontSize: '0.875rem', marginBottom: '1rem' }}>
                  No prediction evaluations recorded yet.
                </p>
                <Link to={`/startups/${startupId}/predictions`}>
                  <Button variant="primary" size="sm">
                    Execute Prediction Now
                  </Button>
                </Link>
              </div>
            )}
          </Card>
        </div>
      )}

      {activeTab === 'financials' && (
        <Card
          title="Financial Telemetry & Balance Variables"
          action={
            <Link to={`/startups/${startupId}/edit`}>
              <Button variant="secondary" size="sm" leftIcon={<Edit3 size={13} />}>
                Edit Financials
              </Button>
            </Link>
          }
        >
          {financial ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem' }}>
              <div className="vt-card" style={{ backgroundColor: 'var(--color-bg-secondary)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>
                  Initial Capital / Investment
                </span>
                <div style={{ fontSize: '1.5rem', fontWeight: 800, marginTop: '0.25rem' }}>
                  {formatINR(financial.initial_investment)}
                </div>
              </div>

              <div className="vt-card" style={{ backgroundColor: 'var(--color-bg-secondary)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>
                  External Funding Raised
                </span>
                <div style={{ fontSize: '1.5rem', fontWeight: 800, marginTop: '0.25rem' }}>
                  {formatINR(financial.funding_raised)}
                </div>
              </div>

              <div className="vt-card" style={{ backgroundColor: 'var(--color-bg-secondary)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>
                  Monthly Revenue
                </span>
                <div style={{ fontSize: '1.5rem', fontWeight: 800, marginTop: '0.25rem' }}>
                  {formatINR(financial.monthly_revenue)}
                </div>
              </div>

              <div className="vt-card" style={{ backgroundColor: 'var(--color-bg-secondary)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>
                  Monthly Expenses
                </span>
                <div style={{ fontSize: '1.5rem', fontWeight: 800, marginTop: '0.25rem' }}>
                  {formatINR(financial.monthly_expenses)}
                </div>
              </div>

              <div className="vt-card" style={{ backgroundColor: 'var(--color-bg-secondary)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>
                  Annual Revenue
                </span>
                <div style={{ fontSize: '1.5rem', fontWeight: 800, marginTop: '0.25rem' }}>
                  {formatINR(financial.annual_revenue)}
                </div>
              </div>

              <div className="vt-card" style={{ backgroundColor: 'var(--color-bg-secondary)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>
                  Estimated Burn Rate
                </span>
                <div style={{ fontSize: '1.5rem', fontWeight: 800, marginTop: '0.25rem' }}>
                  {formatINR(financial.burn_rate)}
                </div>
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '2rem 1rem' }}>
              <p style={{ fontSize: '0.9rem', marginBottom: '1rem' }}>
                No financial parameters recorded for this startup yet.
              </p>
              <Link to={`/startups/${startupId}/edit`}>
                <Button variant="primary" size="sm">
                  Add Financial Details
                </Button>
              </Link>
            </div>
          )}
        </Card>
      )}

      {activeTab === 'team' && (
        <Card
          title="Team & Organizational Telemetry"
          action={
            <Link to={`/startups/${startupId}/edit`}>
              <Button variant="secondary" size="sm" leftIcon={<Edit3 size={13} />}>
                Edit Team
              </Button>
            </Link>
          }
        >
          {team ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem', fontSize: '0.9rem' }}>
              <div>
                <span style={{ color: 'var(--color-text-muted)', fontSize: '0.78rem', display: 'block' }}>Founder Name</span>
                <strong>{team.founder_name || 'Not provided'}</strong>
              </div>

              <div>
                <span style={{ color: 'var(--color-text-muted)', fontSize: '0.78rem', display: 'block' }}>Founder Experience</span>
                <strong>
                  {team.founder_experience_years !== null && team.founder_experience_years !== undefined
                    ? `${team.founder_experience_years} Years`
                    : 'Not provided'}
                </strong>
              </div>

              <div>
                <span style={{ color: 'var(--color-text-muted)', fontSize: '0.78rem', display: 'block' }}>Founder Education</span>
                <strong>{team.founder_education || 'Not provided'}</strong>
              </div>

              <div>
                <span style={{ color: 'var(--color-text-muted)', fontSize: '0.78rem', display: 'block' }}>Total Employee Count</span>
                <strong>
                  {team.employee_count !== null && team.employee_count !== undefined
                    ? `${team.employee_count} Team Members`
                    : 'Not provided'}
                </strong>
              </div>

              <div>
                <span style={{ color: 'var(--color-text-muted)', fontSize: '0.78rem', display: 'block' }}>Technical Co-founder</span>
                <strong>{team.has_technical_cofounder ? 'Yes (Present)' : 'No (Absent)'}</strong>
              </div>

              <div style={{ gridColumn: 'span 2' }}>
                <span style={{ color: 'var(--color-text-muted)', fontSize: '0.78rem', display: 'block' }}>Core Team Skills</span>
                <strong>{team.team_skills || 'None specified'}</strong>
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '2rem 1rem' }}>
              <p style={{ fontSize: '0.9rem', marginBottom: '1rem' }}>No team composition data entered yet.</p>
              <Link to={`/startups/${startupId}/edit`}>
                <Button variant="primary" size="sm">
                  Add Team Details
                </Button>
              </Link>
            </div>
          )}
        </Card>
      )}

      {activeTab === 'location' && (
        <Card
          title="Business Location & Registration Address"
          action={
            <Link to={`/startups/${startupId}/edit`}>
              <Button variant="secondary" size="sm" leftIcon={<Edit3 size={13} />}>
                Edit Location
              </Button>
            </Link>
          }
        >
          {location ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem', fontSize: '0.9rem' }}>
              <div>
                <span style={{ color: 'var(--color-text-muted)', fontSize: '0.78rem', display: 'block' }}>Country</span>
                <strong>{location.country || '—'}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--color-text-muted)', fontSize: '0.78rem', display: 'block' }}>State / Region</span>
                <strong>{location.state || '—'}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--color-text-muted)', fontSize: '0.78rem', display: 'block' }}>City</span>
                <strong>{location.city || '—'}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--color-text-muted)', fontSize: '0.78rem', display: 'block' }}>Postal Pincode</span>
                <strong>{location.pincode || '—'}</strong>
              </div>
              <div style={{ gridColumn: 'span 2' }}>
                <span style={{ color: 'var(--color-text-muted)', fontSize: '0.78rem', display: 'block' }}>Street Address</span>
                <strong>{location.address || '—'}</strong>
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '2rem 1rem' }}>
              <p style={{ fontSize: '0.9rem', marginBottom: '1rem' }}>No physical address on file.</p>
              <Link to={`/startups/${startupId}/edit`}>
                <Button variant="primary" size="sm">
                  Add Location
                </Button>
              </Link>
            </div>
          )}
        </Card>
      )}

      {activeTab === 'land' && (
        <Card
          title="Land & Commercial Premises Utilization"
          action={
            <Link to={`/startups/${startupId}/edit`}>
              <Button variant="secondary" size="sm" leftIcon={<Edit3 size={13} />}>
                Edit Land Details
              </Button>
            </Link>
          }
        >
          {land && land.has_land ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem', fontSize: '0.9rem' }}>
              <div>
                <span style={{ color: 'var(--color-text-muted)', fontSize: '0.78rem', display: 'block' }}>Tenure Status</span>
                <strong style={{ textTransform: 'capitalize' }}>{land.land_status || '—'}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--color-text-muted)', fontSize: '0.78rem', display: 'block' }}>Floor / Land Area</span>
                <strong>{land.land_area_sqft ? `${land.land_area_sqft} sq. ft.` : '—'}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--color-text-muted)', fontSize: '0.78rem', display: 'block' }}>Estimated Property Value</span>
                <strong>{formatINR(land.land_value)}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--color-text-muted)', fontSize: '0.78rem', display: 'block' }}>Monthly Rent / Lease</span>
                <strong>{formatINR(land.monthly_rent)}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--color-text-muted)', fontSize: '0.78rem', display: 'block' }}>Expansion Available</span>
                <strong>{land.expansion_available ? 'Yes' : 'No'}</strong>
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '2rem 1rem' }}>
              <Compass size={28} style={{ color: 'var(--color-text-muted)', marginBottom: '0.5rem' }} />
              <p style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)' }}>
                No dedicated commercial land or manufacturing premises recorded for this startup.
              </p>
            </div>
          )}
        </Card>
      )}

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        title={`Delete ${profile.startup_name}`}
        description="Permanently delete this startup and all its associated telemetry records."
        confirmLabel="Confirm Deletion"
        confirmVariant="danger"
        isConfirmLoading={isDeleting}
        onConfirm={handleDelete}
      >
        <p style={{ fontSize: '0.9rem', marginBottom: '1rem' }}>
          Are you sure you want to delete this startup profile? This action will remove all financial records,
          team information, simulations, AI recommendations, and generated reports.
        </p>
        {deleteError && <div className="alert alert-danger">{deleteError}</div>}
      </Modal>
    </div>
  );
};
