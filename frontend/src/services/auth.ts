/**
 * Authentication API service
 *
 * Provides API methods for user authentication via Supabase.
 */

import { apiClient } from '../lib/apiClient';

/**
 * User and auth type definitions
 */
export interface User {
  id: string;
  email: string;
  name?: string;
  created_at: string;
}

export interface LoginInput {
  email: string;
  password: string;
}

export interface RegisterInput {
  email: string;
  password: string;
  name?: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  expires_at: string;
}

/**
 * Auth API service object
 */
export const authApi = {
  /**
   * Login with email and password
   */
  async login(input: LoginInput): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/login', input);

    // Store token in localStorage
    localStorage.setItem('auth_token', response.data.access_token);

    return response.data;
  },

  /**
   * Register a new user
   */
  async register(input: RegisterInput): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/register', input);

    // Store token in localStorage
    localStorage.setItem('auth_token', response.data.access_token);

    return response.data;
  },

  /**
   * Logout current user
   */
  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout');
    } finally {
      // Always clear token, even if API call fails
      localStorage.removeItem('auth_token');
    }
  },

  /**
   * Get current user profile
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },

  /**
   * Refresh access token
   */
  async refreshToken(refreshToken: string): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });

    // Update token in localStorage
    localStorage.setItem('auth_token', response.data.access_token);

    return response.data;
  },
};
