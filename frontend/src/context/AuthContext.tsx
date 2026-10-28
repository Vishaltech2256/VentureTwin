import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authApi } from '../api/auth';
import {
  UserResponse,
  UserLoginRequest,
  UserRegisterRequest,
  UserUpdateRequest,
} from '../types';
import { normalizeError } from '../utils/errors';

interface AuthContextType {
  user: UserResponse | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  login: (data: UserLoginRequest) => Promise<void>;
  loginOAuth2: (email: string, password: string) => Promise<void>;
  register: (data: UserRegisterRequest) => Promise<void>;
  updateUser: (data: UserUpdateRequest) => Promise<void>;
  refreshProfile: () => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('access_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const clearError = () => setError(null);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setToken(null);
    setUser(null);
    setError(null);
  }, []);

  const refreshProfile = useCallback(async () => {
    try {
      const profile = await authApi.getMe();
      setUser(profile);
      setError(null);
    } catch (err) {
      // If fetching me fails, token may be stale
      logout();
    }
  }, [logout]);

  // Initial auth verification on page load
  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = localStorage.getItem('access_token');
      if (storedToken) {
        try {
          const profile = await authApi.getMe();
          setUser(profile);
          setToken(storedToken);
        } catch {
          logout();
        }
      }
      setIsLoading(false);
    };

    initializeAuth();
  }, [logout]);

  const login = async (credentials: UserLoginRequest) => {
    setIsLoading(true);
    setError(null);
    try {
      const tokens = await authApi.login(credentials);
      localStorage.setItem('access_token', tokens.access_token);
      localStorage.setItem('refresh_token', tokens.refresh_token);
      setToken(tokens.access_token);
      const profile = await authApi.getMe();
      setUser(profile);
    } catch (err) {
      const norm = normalizeError(err);
      setError(norm.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const loginOAuth2 = async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const tokens = await authApi.loginOAuth2(email, password);
      localStorage.setItem('access_token', tokens.access_token);
      localStorage.setItem('refresh_token', tokens.refresh_token);
      setToken(tokens.access_token);
      const profile = await authApi.getMe();
      setUser(profile);
    } catch (err) {
      const norm = normalizeError(err);
      setError(norm.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: UserRegisterRequest) => {
    setIsLoading(true);
    setError(null);
    try {
      await authApi.register(data);
      // Auto login following successful registration
      await login({ email: data.email, password: data.password });
    } catch (err) {
      const norm = normalizeError(err);
      setError(norm.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const updateUser = async (data: UserUpdateRequest) => {
    setError(null);
    try {
      const updated = await authApi.updateMe(data);
      setUser(updated);
    } catch (err) {
      const norm = normalizeError(err);
      setError(norm.message);
      throw err;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        error,
        login,
        loginOAuth2,
        register,
        updateUser,
        refreshProfile,
        logout,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
