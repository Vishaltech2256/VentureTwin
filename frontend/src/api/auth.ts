import client from './client';
import {
  UserRegisterRequest,
  UserLoginRequest,
  TokenResponse,
  UserResponse,
  UserUpdateRequest,
  RefreshTokenRequest,
} from '../types';

export const authApi = {
  /** Register a new user */
  register: async (data: UserRegisterRequest): Promise<UserResponse> => {
    const res = await client.post<UserResponse>('/auth/register', data);
    return res.data;
  },

  /** Sign in with JSON (Email + Password) */
  login: async (data: UserLoginRequest): Promise<TokenResponse> => {
    const res = await client.post<TokenResponse>('/auth/login', data);
    return res.data;
  },

  /** Sign in via OAuth2 Password form-encoded endpoint */
  loginOAuth2: async (email: string, password: string): Promise<TokenResponse> => {
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);
    const res = await client.post<TokenResponse>('/auth/token', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return res.data;
  },

  /** Get current authenticated user profile */
  getMe: async (): Promise<UserResponse> => {
    const res = await client.get<UserResponse>('/auth/me');
    return res.data;
  },

  /** Update current authenticated user profile */
  updateMe: async (data: UserUpdateRequest): Promise<UserResponse> => {
    const res = await client.patch<UserResponse>('/auth/me', data);
    return res.data;
  },

  /** Refresh access token using refresh token */
  refresh: async (refreshToken: string): Promise<TokenResponse> => {
    const res = await client.post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    } as RefreshTokenRequest);
    return res.data;
  },
};
