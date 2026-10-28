import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { AppLayout } from './components/layout/AppLayout';

import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPage } from './pages/DashboardPage';
import { StartupsPage } from './pages/StartupsPage';
import { CreateStartupPage } from './pages/CreateStartupPage';
import { StartupDetailPage } from './pages/StartupDetailPage';
import { EditStartupPage } from './pages/EditStartupPage';
import { PredictionsPage } from './pages/PredictionsPage';
import { SuggestionsPage } from './pages/SuggestionsPage';
import { ReportsPage } from './pages/ReportsPage';
import { AccountPage } from './pages/AccountPage';

const AppRoutes: React.FC = () => {
  const { user } = useAuth();

  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<LandingPage />} />
      <Route
        path="/login"
        element={user ? <Navigate to="/dashboard" replace /> : <LoginPage />}
      />
      <Route
        path="/register"
        element={user ? <Navigate to="/dashboard" replace /> : <RegisterPage />}
      />

      {/* Authenticated Application Shell */}
      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/startups" element={<StartupsPage />} />
        <Route path="/startups/new" element={<CreateStartupPage />} />
        <Route path="/startups/:startupId" element={<StartupDetailPage />} />
        <Route path="/startups/:startupId/edit" element={<EditStartupPage />} />
        <Route path="/startups/:startupId/predictions" element={<PredictionsPage />} />
        <Route path="/startups/:startupId/suggestions" element={<SuggestionsPage />} />
        <Route path="/startups/:startupId/reports" element={<ReportsPage />} />
        <Route path="/predictions" element={<PredictionsPage />} />
        <Route path="/suggestions" element={<SuggestionsPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/account" element={<AccountPage />} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to={user ? "/dashboard" : "/"} replace />} />
    </Routes>
  );
};

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
