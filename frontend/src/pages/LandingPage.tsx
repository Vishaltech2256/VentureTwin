import React from 'react';
import { Link } from 'react-router-dom';
import {
  Layers,
  ArrowRight,
  TrendingUp,
  Sparkles,
  FileText,
  ShieldCheck,
  ChevronRight,
  Building,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/Button';

export const LandingPage: React.FC = () => {
  const { user } = useAuth();

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#FFFFFF' }}>
      {/* Top Navbar */}
      <header
        style={{
          borderBottom: '1px solid var(--color-border)',
          backgroundColor: '#FFFFFF',
          position: 'sticky',
          top: 0,
          zIndex: 40,
        }}
      >
        <div
          style={{
            maxWidth: '1200px',
            margin: '0 auto',
            padding: '1.25rem 2rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div
              style={{
                width: 32,
                height: 32,
                backgroundColor: '#111111',
                color: '#FFFFFF',
                borderRadius: '6px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Layers size={18} />
            </div>
            <span style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '-0.03em', color: '#111111' }}>
              VentureTwin
            </span>
            <span className="brand-badge">Enterprise</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            {user ? (
              <Link to="/dashboard">
                <Button variant="primary" size="sm" rightIcon={<ArrowRight size={14} />}>
                  Go to Dashboard
                </Button>
              </Link>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="secondary" size="sm">
                    Sign In
                  </Button>
                </Link>
                <Link to="/register">
                  <Button variant="primary" size="sm" rightIcon={<ChevronRight size={14} />}>
                    Get Started
                  </Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section
        style={{
          padding: '6rem 2rem 5rem',
          maxWidth: '1000px',
          margin: '0 auto',
          textAlign: 'center',
        }}
      >
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.35rem 0.85rem',
            borderRadius: 'var(--radius-full)',
            backgroundColor: '#F5F5F5',
            border: '1px solid #E5E5E5',
            fontSize: '0.8rem',
            fontWeight: 600,
            marginBottom: '2rem',
            color: '#111111',
          }}
        >
          <span style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: '#111111' }} />
          Startup Digital Twin Intelligence
        </div>

        <h1
          style={{
            fontSize: 'clamp(2.5rem, 5vw, 3.75rem)',
            fontWeight: 800,
            letterSpacing: '-0.04em',
            lineHeight: 1.15,
            color: '#111111',
            marginBottom: '1.5rem',
          }}
        >
          Understand Your Startup Before You Scale.
        </h1>

        <p
          style={{
            fontSize: 'clamp(1.05rem, 2vw, 1.25rem)',
            color: '#666666',
            lineHeight: 1.6,
            maxWidth: '720px',
            margin: '0 auto 2.5rem',
          }}
        >
          Bring your startup information together, explore available financial projections,
          and review data-driven recommendations through VentureTwin.
        </p>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          {user ? (
            <Link to="/dashboard">
              <Button size="lg" variant="primary" rightIcon={<ArrowRight size={18} />}>
                Open Dashboard
              </Button>
            </Link>
          ) : (
            <>
              <Link to="/register">
                <Button size="lg" variant="primary" rightIcon={<ArrowRight size={18} />}>
                  Get Started Free
                </Button>
              </Link>
              <Link to="/login">
                <Button size="lg" variant="secondary">
                  Founder Sign In
                </Button>
              </Link>
            </>
          )}
        </div>
      </section>

      {/* Feature Capabilities Grid */}
      <section
        style={{
          backgroundColor: '#F5F5F5',
          borderTop: '1px solid #E5E5E5',
          borderBottom: '1px solid #E5E5E5',
          padding: '5rem 2rem',
        }}
      >
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '3.5rem' }}>
            <h2 style={{ fontSize: '2rem', fontWeight: 800, color: '#111111' }}>
              Built for Grounded Business Analytics
            </h2>
            <p style={{ marginTop: '0.5rem', color: '#666666' }}>
              Fully integrated with real rule-based backend algorithms and verified data schemas.
            </p>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
              gap: '1.5rem',
            }}
          >
            <div className="vt-card">
              <div style={{ width: 40, height: 40, borderRadius: '6px', backgroundColor: '#111111', color: '#FFFFFF', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem' }}>
                <Building size={20} />
              </div>
              <h3 style={{ fontSize: '1.15rem', marginBottom: '0.5rem' }}>Startup Modeling</h3>
              <p style={{ fontSize: '0.875rem' }}>
                Capture comprehensive operational data: foundational profiles, financial telemetry, team composition, geographical address, and land utilization.
              </p>
            </div>

            <div className="vt-card">
              <div style={{ width: 40, height: 40, borderRadius: '6px', backgroundColor: '#111111', color: '#FFFFFF', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem' }}>
                <TrendingUp size={20} />
              </div>
              <h3 style={{ fontSize: '1.15rem', marginBottom: '0.5rem' }}>Prediction Engine</h3>
              <p style={{ fontSize: '0.875rem' }}>
                Transparent rule-based scoring evaluating revenue versus expenses, capital adequacy, team capability, and break-even timelines.
              </p>
            </div>

            <div className="vt-card">
              <div style={{ width: 40, height: 40, borderRadius: '6px', backgroundColor: '#111111', color: '#FFFFFF', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem' }}>
                <Sparkles size={20} />
              </div>
              <h3 style={{ fontSize: '1.15rem', marginBottom: '0.5rem' }}>AI Recommendations</h3>
              <p style={{ fontSize: '0.875rem' }}>
                Contextual strategic suggestions generated directly from the latest prediction results, prioritized by impact and categorized for execution.
              </p>
            </div>

            <div className="vt-card">
              <div style={{ width: 40, height: 40, borderRadius: '6px', backgroundColor: '#111111', color: '#FFFFFF', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem' }}>
                <FileText size={20} />
              </div>
              <h3 style={{ fontSize: '1.15rem', marginBottom: '0.5rem' }}>Executive PDF Reports</h3>
              <p style={{ fontSize: '0.875rem' }}>
                Generate official executive reports compiled via ReportLab with complete financial breakdowns, prediction summaries, and investor-ready structure.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Assurance / Trust Banner */}
      <section style={{ padding: '4rem 2rem', maxWidth: '900px', margin: '0 auto', textAlign: 'center' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem', color: '#111111' }}>
          <ShieldCheck size={24} />
          <span style={{ fontWeight: 700, fontSize: '1.1rem' }}>No Fabrications. No Black Box Hallucinations.</span>
        </div>
        <p style={{ fontSize: '0.9rem', color: '#666666' }}>
          VentureTwin uses deterministic calculations and authenticated REST APIs to ensure that every metric shown corresponds strictly to your verified startup data.
        </p>
      </section>

      {/* Footer */}
      <footer
        style={{
          marginTop: 'auto',
          borderTop: '1px solid #E5E5E5',
          backgroundColor: '#FFFFFF',
          padding: '2.5rem 2rem',
        }}
      >
        <div
          style={{
            maxWidth: '1200px',
            margin: '0 auto',
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: '1.5rem',
            fontSize: '0.85rem',
            color: '#666666',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span style={{ fontWeight: 800, color: '#111111' }}>VentureTwin</span>
            <span>&copy; {new Date().getFullYear()} VentureTwin Inc. All rights reserved.</span>
          </div>

          <div style={{ display: 'flex', gap: '1.5rem' }}>
            <Link to="/login" style={{ color: '#111111', fontWeight: 500 }}>Sign In</Link>
            <Link to="/register" style={{ color: '#111111', fontWeight: 500 }}>Register</Link>
            <span style={{ color: '#888888' }}>FastAPI v1 API Connected</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
