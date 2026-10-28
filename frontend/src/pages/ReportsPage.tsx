import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  FileText,
  Download,
  Plus,
  AlertCircle,
  Building2,
  Calendar,
  CheckCircle2,
  ArrowLeft,
  Loader2,
} from 'lucide-react';
import { reportApi } from '../api/reports';
import { startupApi } from '../api/startups';
import { useApp } from '../components/layout/AppLayout';
import { ReportResponse, StartupProfileResponse } from '../types';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { LoadingState } from '../components/feedback/LoadingState';
import { ErrorState } from '../components/feedback/ErrorState';
import { EmptyState } from '../components/feedback/EmptyState';
import { formatDate, formatDateTime } from '../utils/formatters';
import { normalizeError } from '../utils/errors';

export const ReportsPage: React.FC = () => {
  const { startupId } = useParams<{ startupId: string }>();
  const { startups, activeStartupId, setActiveStartupId } = useApp();

  const effectiveId = startupId
    ? Number(startupId)
    : (activeStartupId ?? (startups.length > 0 ? startups[0].startup_id : null));

  const [currentStartup, setCurrentStartup] = useState<StartupProfileResponse | null>(null);
  const [reports, setReports] = useState<ReportResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [downloadingId, setDownloadingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [genSuccess, setGenSuccess] = useState<string | null>(null);

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
        reportApi.list(effectiveId),
      ]);
      setCurrentStartup(profile);
      setReports(list);
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
      const newReport = await reportApi.generate(effectiveId);
      setReports((prev) => [newReport, ...prev]);
      setGenSuccess('Executive PDF report generated and archived successfully.');
      setTimeout(() => setGenSuccess(null), 4000);
    } catch (err) {
      const norm = normalizeError(err);
      setError(norm.message);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = async (report: ReportResponse) => {
    setDownloadingId(report.report_id);
    setError(null);
    try {
      const filename = `${report.title.replace(/[^a-zA-Z0-9_-]/g, '_')}_#${report.report_id}.pdf`;
      await reportApi.downloadPdf(report.report_id, filename);
    } catch (err) {
      const norm = normalizeError(err);
      setError(`Failed to download report: ${norm.message}`);
    } finally {
      setDownloadingId(null);
    }
  };

  if (!effectiveId) {
    return (
      <EmptyState
        icon={<Building2 size={28} />}
        title="No Startup Selected"
        description="Choose a startup from the registry or create a new profile to inspect and generate executive reports."
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
    return <LoadingState message="Loading archived reports..." />;
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
            <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Executive Reports</h1>
            <p style={{ marginTop: '0.25rem' }}>
              Venture: <strong>{currentStartup?.startup_name}</strong> • Investor-ready ReportLab PDF exports.
            </p>
          </div>

          <Button
            variant="primary"
            onClick={handleGenerate}
            isLoading={isGenerating}
            leftIcon={<Plus size={16} />}
          >
            Generate New PDF Report
          </Button>
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
          <div>{error}</div>
        </div>
      )}

      {/* Reports Archive */}
      {reports.length === 0 ? (
        <EmptyState
          icon={<FileText size={28} />}
          title="No Reports Generated Yet"
          description="Click 'Generate New PDF Report' to compile your startup's financial profile, predictions, and overview into an official ReportLab PDF document."
          actionLabel="Generate PDF Report"
          onAction={handleGenerate}
          actionIcon={<Plus size={16} />}
        />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {reports.map((rep) => {
            const isThisDownloading = downloadingId === rep.report_id;

            return (
              <div
                key={rep.report_id}
                className="vt-card"
                style={{
                  display: 'flex',
                  flexWrap: 'wrap',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: '1rem',
                  padding: '1.25rem 1.5rem',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <div
                    style={{
                      width: 44,
                      height: 44,
                      borderRadius: 'var(--radius-sm)',
                      backgroundColor: 'var(--color-bg-secondary)',
                      border: '1px solid var(--color-border)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#111111',
                      flexShrink: 0,
                    }}
                  >
                    <FileText size={22} />
                  </div>

                  <div>
                    <h3 style={{ fontSize: '1.05rem', fontWeight: 700 }}>{rep.title}</h3>
                    <div style={{ display: 'flex', gap: '0.75rem', fontSize: '0.8rem', color: 'var(--color-text-muted)', marginTop: '0.2rem' }}>
                      <span>Report #{rep.report_id}</span>
                      <span>•</span>
                      <span>Type: {rep.report_type}</span>
                      {rep.prediction_id && (
                        <>
                          <span>•</span>
                          <span>Prediction #{rep.prediction_id}</span>
                        </>
                      )}
                      <span>•</span>
                      <span>{formatDateTime(rep.created_at)}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => handleDownload(rep)}
                    disabled={isThisDownloading}
                    leftIcon={
                      isThisDownloading ? (
                        <Loader2 size={14} className="animate-spin" />
                      ) : (
                        <Download size={14} />
                      )
                    }
                  >
                    {isThisDownloading ? 'Downloading...' : 'Download PDF'}
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
