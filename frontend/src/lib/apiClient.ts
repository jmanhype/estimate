/**
 * Axios API client with interceptors
 *
 * Provides a configured Axios instance for making API requests with:
 * - Automatic authentication token injection
 * - Request/response logging in development
 * - Error handling and transformation
 * - Retry logic for transient failures
 */

import axios, { type AxiosError, type AxiosRequestConfig, type InternalAxiosRequestConfig } from 'axios';

/**
 * Base API client configuration
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
const API_TIMEOUT = 30000; // 30 seconds

/**
 * Create Axios instance with default configuration
 */
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor - adds authentication token to all requests
 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Get auth token from localStorage (will be replaced with proper auth context)
    const token = localStorage.getItem('auth_token');

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Log request in development
    if (import.meta.env.DEV) {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
        params: config.params,
        data: config.data,
      });
    }

    return config;
  },
  (error: AxiosError) => {
    if (import.meta.env.DEV) {
      console.error('[API Request Error]', error);
    }
    return Promise.reject(error);
  },
);

/**
 * Response interceptor - handles errors and logging
 */
apiClient.interceptors.response.use(
  (response) => {
    // Log response in development
    if (import.meta.env.DEV) {
      console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, {
        status: response.status,
        data: response.data,
      });
    }

    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

    // Log error in development
    if (import.meta.env.DEV) {
      console.error('[API Response Error]', {
        url: error.config?.url,
        method: error.config?.method,
        status: error.response?.status,
        message: error.message,
        data: error.response?.data,
      });
    }

    // Handle 401 Unauthorized - redirect to login
    if (error.response?.status === 401) {
      // Clear auth token
      localStorage.removeItem('auth_token');

      // Redirect to login if not already there
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }

      return Promise.reject(error);
    }

    // Handle 403 Forbidden - subscription required
    if (error.response?.status === 403) {
      // Could redirect to subscription page or show upgrade modal
      // For now, just reject
      return Promise.reject(error);
    }

    // Handle 500+ server errors with retry logic (only once)
    if (
      error.response?.status &&
      error.response.status >= 500 &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;

      // Wait 1 second before retrying
      await new Promise((resolve) => setTimeout(resolve, 1000));

      try {
        return await apiClient(originalRequest);
      } catch (retryError) {
        return Promise.reject(retryError);
      }
    }

    // Transform error for better error messages
    const errorMessage =
      (error.response?.data as { detail?: string })?.detail ||
      error.message ||
      'An unexpected error occurred';

    return Promise.reject(new Error(errorMessage));
  },
);

/**
 * Type-safe API error class
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: unknown,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Helper function to check if error is an API error
 */
export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

/**
 * Helper function to extract error message from unknown error
 */
export function getErrorMessage(error: unknown): string {
  if (isApiError(error)) {
    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  if (typeof error === 'string') {
    return error;
  }

  return 'An unexpected error occurred';
}
