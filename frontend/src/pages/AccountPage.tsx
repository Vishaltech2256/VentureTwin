import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  User as UserIcon,
  Mail,
  Shield,
  LogOut,
  Save,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card } from '../components/ui/Card';
import { normalizeError } from '../utils/errors';

export const AccountPage: React.FC = () => {
  const { user, updateUser, logout } = useAuth();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState(user?.full_name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (user) {
      setFullName(user.full_name || '');
      setEmail(user.email || '');
    }
  }, [user]);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setSaveSuccess(false);

    if (!email.trim()) {
      setErrorMessage('Email address cannot be empty.');
      return;
    }

    setIsSaving(true);
    try {
      await updateUser({
        full_name: fullName.trim() || null,
        email: email.trim(),
      });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3500);
    } catch (err) {
      const norm = normalizeError(err);
      setErrorMessage(norm.message);
    } finally {
      setIsSaving(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div style={{ maxWidth: '680px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Account Settings</h1>
        <p style={{ marginTop: '0.25rem' }}>
          Manage your founder profile credentials and authentication session.
        </p>
      </div>

      {saveSuccess && (
        <div className="alert alert-success animate-fade-in" role="alert">
          <CheckCircle2 size={18} style={{ flexShrink: 0, marginTop: 2 }} />
          <div>Profile updated successfully!</div>
        </div>
      )}

      {errorMessage && (
        <div className="alert alert-danger" role="alert">
          <AlertCircle size={18} style={{ flexShrink: 0, marginTop: 2 }} />
          <div>{errorMessage}</div>
        </div>
      )}

      {/* Account Info Card */}
      <Card title="Founder Profile">
        <form onSubmit={handleUpdate} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <Input
            label="Full Name"
            type="text"
            placeholder="e.g. Elena Rostova"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
          />

          <Input
            label="Email Address"
            type="email"
            placeholder="name@company.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />


          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
            <Button
              type="submit"
              variant="primary"
              isLoading={isSaving}
              leftIcon={<Save size={15} />}
            >
              Update Profile
            </Button>
          </div>
        </form>
      </Card>

      {/* Session / Sign Out Card */}
      <Card title="Authentication Session">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h4 style={{ fontSize: '0.95rem' }}>Sign Out</h4>
            <p style={{ fontSize: '0.85rem' }}>
              Terminate your active session and clear cached credentials from this browser.
            </p>
          </div>

          <Button
            variant="secondary"
            onClick={handleLogout}
            leftIcon={<LogOut size={15} />}
          >
            Sign Out
          </Button>
        </div>
      </Card>
    </div>
  );
};
