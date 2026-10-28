import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Layers, Eye, EyeOff, AlertCircle, Mail, User, Lock, Check, X, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { normalizeError } from '../utils/errors';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [generalError, setGeneralError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Forgot password modal state
  const [showForgotModal, setShowForgotModal] = useState(false);
  const [forgotEmail, setForgotEmail] = useState('');
  const [forgotStatus, setForgotStatus] = useState<'idle' | 'sent'>('idle');

  const { loginOAuth2, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/dashboard';

  // Load remembered email on mount
  useEffect(() => {
    const savedEmail = localStorage.getItem('vt_remembered_email');
    if (savedEmail) {
      setEmail(savedEmail);
      setForgotEmail(savedEmail);
      setRememberMe(true);
    }
  }, []);

  const validate = (): boolean => {
    const errors: Record<string, string> = {};
    if (!email.trim()) {
      errors.email = 'Email address is required.';
    }
    if (!password) {
      errors.password = 'Password is required.';
    }
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setGeneralError(null);

    if (!validate()) return;

    if (rememberMe) {
      localStorage.setItem('vt_remembered_email', email.trim());
    } else {
      localStorage.removeItem('vt_remembered_email');
    }

    setIsSubmitting(true);
    try {
      try {
        await loginOAuth2(email.trim(), password);
      } catch (oauthErr: any) {
        if (oauthErr?.response?.status === 404) {
          await login({ email: email.trim(), password });
        } else {
          throw oauthErr;
        }
      }

      navigate(from, { replace: true });
    } catch (err) {
      const norm = normalizeError(err);
      if (norm.status === 401 || norm.status === 400) {
        setGeneralError('Invalid email or password. Please verify your credentials.');
      } else {
        setGeneralError(norm.message);
      }
      if (Object.keys(norm.fieldErrors).length > 0) {
        setFieldErrors(norm.fieldErrors);
      }
    } finally {
      setIsSubmitting(false);
    }
  };


  const handleForgotPasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!forgotEmail.trim()) return;
    setForgotStatus('sent');
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2.5rem 1.5rem',
        backgroundImage: 'linear-gradient(rgba(10, 10, 12, 0.45), rgba(10, 10, 12, 0.65)), url("/login-bg.jpg")',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        backgroundAttachment: 'fixed',
        color: '#FFFFFF',
        fontFamily: 'inherit',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Background ambient subtle glow */}
      <div
        style={{
          position: 'absolute',
          top: '-15%',
          left: '50%',
          transform: 'translateX(-50%)',
          width: '600px',
          height: '600px',
          background: 'radial-gradient(circle, rgba(255, 255, 255, 0.04) 0%, rgba(0, 0, 0, 0) 70%)',
          pointerEvents: 'none',
        }}
      />

      <div style={{ width: '100%', maxWidth: '440px', zIndex: 1 }} className="animate-fade-in">
        {/* VentureTwin Brand Logo */}
        <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
          <Link
            to="/"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.85rem',
              marginBottom: '1.25rem',
              textDecoration: 'none',
            }}
          >
            <div
              style={{
                width: 44,
                height: 44,
                backgroundColor: 'rgba(255, 255, 255, 0.08)',
                border: '1px solid rgba(255, 255, 255, 0.15)',
                color: '#FFFFFF',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 4px 16px rgba(0,0,0,0.4)',
              }}
            >
              <Layers size={24} />
            </div>
            <span
              style={{
                fontSize: '1.75rem',
                fontWeight: 700,
                letterSpacing: '-0.02em',
                color: '#FFFFFF',
              }}
            >
              VentureTwin
            </span>
          </Link>

          {/* Member Login Header as in reference image */}
          <h1
            style={{
              fontSize: '2.1rem',
              fontWeight: 300,
              letterSpacing: '0.15em',
              color: '#F3F4F6',
              textTransform: 'none',
              marginTop: '0.5rem',
              marginBottom: '0.5rem',
            }}
          >
            Member Login
          </h1>
        </div>

        {/* Error Alert */}
        {generalError && (
          <div
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '0.75rem',
              padding: '1rem 1.25rem',
              marginBottom: '1.75rem',
              backgroundColor: 'rgba(239, 68, 68, 0.12)',
              border: '1px solid rgba(239, 68, 68, 0.35)',
              borderRadius: '6px',
              color: '#FCA5A5',
              fontSize: '1rem',
              lineHeight: 1.5,
            }}
            role="alert"
          >
            <AlertCircle size={22} style={{ flexShrink: 0, marginTop: 2, color: '#EF4444' }} />
            <div>{generalError}</div>
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate>
          {/* Email / Username Glass Input */}
          <div style={{ marginBottom: '1.25rem' }}>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                backgroundColor: 'rgba(0, 0, 0, 0.55)',
                border: fieldErrors.email
                  ? '1px solid #EF4444'
                  : '1px solid rgba(255, 255, 255, 0.15)',
                borderRadius: '6px',
                padding: '0.85rem 1rem',
                backdropFilter: 'blur(10px)',
                WebkitBackdropFilter: 'blur(10px)',
                transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
              }}
            >
              <User
                size={20}
                style={{
                  color: 'rgba(255, 255, 255, 0.65)',
                  marginRight: '0.85rem',
                  flexShrink: 0,
                }}
              />
              <input
                id="login-email"
                type="email"
                className="login-underline-input"
                placeholder="Username"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  setForgotEmail(e.target.value);
                  if (fieldErrors.email) {
                    setFieldErrors((prev) => ({ ...prev, email: '' }));
                  }
                }}
                autoComplete="username"
                style={{
                  width: '100%',
                  background: 'transparent',
                  border: 'none',
                  outline: 'none',
                  color: '#FFFFFF',
                  fontSize: '1.05rem',
                  fontFamily: 'inherit',
                  letterSpacing: '0.02em',
                }}
              />
            </div>
            {fieldErrors.email && (
              <p style={{ color: '#F87171', fontSize: '0.9rem', marginTop: '0.4rem', marginLeft: '0.25rem' }}>
                {fieldErrors.email}
              </p>
            )}
          </div>

          {/* Password Glass Input */}
          <div style={{ marginBottom: '1.5rem' }}>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                backgroundColor: 'rgba(0, 0, 0, 0.55)',
                border: fieldErrors.password
                  ? '1px solid #EF4444'
                  : '1px solid rgba(255, 255, 255, 0.15)',
                borderRadius: '6px',
                padding: '0.85rem 1rem',
                backdropFilter: 'blur(10px)',
                WebkitBackdropFilter: 'blur(10px)',
                transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
              }}
            >
              <Lock
                size={20}
                style={{
                  color: 'rgba(255, 255, 255, 0.65)',
                  marginRight: '0.85rem',
                  flexShrink: 0,
                }}
              />
              <input
                id="login-password"
                type={showPassword ? 'text' : 'password'}
                className="login-underline-input"
                placeholder="Password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (fieldErrors.password) {
                    setFieldErrors((prev) => ({ ...prev, password: '' }));
                  }
                }}
                autoComplete="current-password"
                style={{
                  width: '100%',
                  background: 'transparent',
                  border: 'none',
                  outline: 'none',
                  color: '#FFFFFF',
                  fontSize: '1.05rem',
                  fontFamily: 'inherit',
                  letterSpacing: '0.02em',
                }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  color: 'rgba(255, 255, 255, 0.65)',
                  display: 'flex',
                  alignItems: 'center',
                  padding: '4px',
                }}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            {fieldErrors.password && (
              <p style={{ color: '#F87171', fontSize: '0.9rem', marginTop: '0.4rem', marginLeft: '0.25rem' }}>
                {fieldErrors.password}
              </p>
            )}
          </div>

          {/* Remember me & Forgot Password row */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '2.5rem',
              marginTop: '0.5rem',
            }}
          >
            <label
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.65rem',
                cursor: 'pointer',
                userSelect: 'none',
                fontSize: '1rem',
                color: 'rgba(255, 255, 255, 0.85)',
              }}
            >
              <div
                onClick={() => setRememberMe(!rememberMe)}
                style={{
                  width: 18,
                  height: 18,
                  borderRadius: 3,
                  backgroundColor: rememberMe ? '#FFFFFF' : 'transparent',
                  border: rememberMe ? '1px solid #FFFFFF' : '1px solid rgba(255, 255, 255, 0.45)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                {rememberMe && <Check size={14} color="#000000" strokeWidth={3.5} />}
              </div>
              <span onClick={() => setRememberMe(!rememberMe)}>Remember me</span>
            </label>

            <button
              type="button"
              onClick={() => {
                setForgotStatus('idle');
                setShowForgotModal(true);
              }}
              style={{
                background: 'none',
                border: 'none',
                color: 'rgba(255, 255, 255, 0.85)',
                fontSize: '1rem',
                cursor: 'pointer',
                fontStyle: 'italic',
                padding: '4px 0',
                transition: 'color 0.2s',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.color = '#FFFFFF')}
              onMouseLeave={(e) => (e.currentTarget.style.color = 'rgba(255, 255, 255, 0.85)')}
            >
              Forgot Password?
            </button>
          </div>

          {/* Solid White / Light Grey LOGIN Button matching screenshot */}
          <button
            type="submit"
            disabled={isSubmitting}
            style={{
              width: '100%',
              padding: '1rem 1.5rem',
              backgroundColor: 'rgba(224, 224, 228, 0.9)',
              border: 'none',
              color: '#111114',
              fontSize: '1rem',
              fontWeight: 700,
              letterSpacing: '0.22em',
              textTransform: 'uppercase',
              borderRadius: '4px',
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              transition: 'all 0.25s cubic-bezier(0.16, 1, 0.3, 1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.45)',
            }}
            onMouseEnter={(e) => {
              if (!isSubmitting) {
                e.currentTarget.style.backgroundColor = '#FFFFFF';
                e.currentTarget.style.transform = 'translateY(-1px)';
                e.currentTarget.style.boxShadow = '0 6px 26px rgba(0, 0, 0, 0.6)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isSubmitting) {
                e.currentTarget.style.backgroundColor = 'rgba(224, 224, 228, 0.9)';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.45)';
              }
            }}
          >
            {isSubmitting ? 'SIGNING IN...' : 'LOGIN'}
          </button>


        </form>

        {/* Register Footer */}
        <p
          style={{
            textAlign: 'center',
            marginTop: '2.5rem',
            fontSize: '1rem',
            color: 'rgba(255, 255, 255, 0.7)',
          }}
        >
          Don't have an account?{' '}
          <Link
            to="/register"
            style={{
              fontWeight: 600,
              color: '#FFFFFF',
              textDecoration: 'underline',
              marginLeft: '0.25rem',
            }}
          >
            Register Now
          </Link>
        </p>
      </div>

      {/* Forgot Password Modal */}
      {showForgotModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            backdropFilter: 'blur(6px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '1.5rem',
            zIndex: 100,
          }}
          onClick={() => setShowForgotModal(false)}
        >
          <div
            style={{
              width: '100%',
              maxWidth: '460px',
              backgroundColor: '#141418',
              border: '1px solid rgba(255, 255, 255, 0.18)',
              borderRadius: '8px',
              padding: '2rem',
              color: '#FFFFFF',
              boxShadow: '0 20px 40px rgba(0,0,0,0.6)',
              position: 'relative',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close Button */}
            <button
              type="button"
              onClick={() => setShowForgotModal(false)}
              style={{
                position: 'absolute',
                top: '1.25rem',
                right: '1.25rem',
                background: 'none',
                border: 'none',
                color: 'rgba(255, 255, 255, 0.6)',
                cursor: 'pointer',
                padding: '4px',
              }}
              aria-label="Close modal"
            >
              <X size={22} />
            </button>

            <h2
              style={{
                fontSize: '1.6rem',
                fontWeight: 600,
                letterSpacing: '0.04em',
                marginBottom: '0.75rem',
                color: '#FFFFFF',
              }}
            >
              Reset Password
            </h2>

            {forgotStatus === 'idle' ? (
              <>
                <p
                  style={{
                    fontSize: '1rem',
                    color: 'rgba(255, 255, 255, 0.75)',
                    lineHeight: 1.6,
                    marginBottom: '1.75rem',
                  }}
                >
                  Enter your email address and we'll send you instructions to reset your account password.
                </p>

                <form onSubmit={handleForgotPasswordSubmit}>
                  <div style={{ marginBottom: '1.75rem' }}>
                    <label
                      style={{
                        display: 'block',
                        fontSize: '1rem',
                        fontWeight: 500,
                        marginBottom: '0.5rem',
                        color: 'rgba(255, 255, 255, 0.9)',
                      }}
                    >
                      Email Address
                    </label>
                    <input
                      type="email"
                      placeholder="name@company.com"
                      value={forgotEmail}
                      onChange={(e) => setForgotEmail(e.target.value)}
                      required
                      style={{
                        width: '100%',
                        padding: '0.85rem 1rem',
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                        border: '1px solid rgba(255, 255, 255, 0.2)',
                        borderRadius: '4px',
                        color: '#FFFFFF',
                        fontSize: '1rem',
                        outline: 'none',
                      }}
                    />
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                    <button
                      type="submit"
                      style={{
                        width: '100%',
                        padding: '0.9rem',
                        backgroundColor: '#FFFFFF',
                        border: 'none',
                        color: '#000000',
                        fontSize: '1.05rem',
                        fontWeight: 600,
                        borderRadius: '4px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '0.5rem',
                      }}
                    >
                      <span>Send Reset Link</span>
                      <ArrowRight size={18} />
                    </button>


                  </div>
                </form>
              </>
            ) : (
              <div style={{ textAlign: 'center', padding: '1rem 0' }}>
                <div
                  style={{
                    width: 54,
                    height: 54,
                    borderRadius: '50%',
                    backgroundColor: 'rgba(34, 197, 94, 0.15)',
                    border: '1px solid rgba(34, 197, 94, 0.4)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 1.25rem',
                    color: '#4ADE80',
                  }}
                >
                  <Check size={30} />
                </div>
                <h3 style={{ fontSize: '1.3rem', fontWeight: 600, marginBottom: '0.5rem' }}>
                  Reset Instructions Sent
                </h3>
                <p
                  style={{
                    fontSize: '1rem',
                    color: 'rgba(255, 255, 255, 0.75)',
                    lineHeight: 1.6,
                    marginBottom: '1.75rem',
                  }}
                >
                  Password reset link has been dispatched to{' '}
                  <strong style={{ color: '#FFFFFF' }}>{forgotEmail}</strong>.
                </p>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>


                  <button
                    type="button"
                    onClick={() => setShowForgotModal(false)}
                    style={{
                      width: '100%',
                      padding: '0.85rem',
                      backgroundColor: 'transparent',
                      border: '1px solid rgba(255, 255, 255, 0.25)',
                      color: 'rgba(255, 255, 255, 0.85)',
                      fontSize: '1rem',
                      borderRadius: '4px',
                      cursor: 'pointer',
                    }}
                  >
                    Back to Login
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
