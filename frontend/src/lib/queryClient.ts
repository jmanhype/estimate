/**
 * React Query client configuration
 *
 * Provides centralized configuration for API data fetching and caching.
 */

import { QueryClient, type DefaultOptions } from '@tanstack/react-query';

/**
 * Default query options for all queries
 */
const defaultOptions: DefaultOptions = {
  queries: {
    // Cache time: how long unused data stays in cache (5 minutes)
    gcTime: 1000 * 60 * 5,

    // Stale time: how long data is considered fresh (1 minute)
    staleTime: 1000 * 60,

    // Retry configuration
    retry: 1, // Retry failed requests once
    retryDelay: (attemptIndex: number) => Math.min(1000 * 2 ** attemptIndex, 30000),

    // Refetch configuration
    refetchOnWindowFocus: false, // Don't refetch when window regains focus
    refetchOnReconnect: true, // Refetch when network reconnects
    refetchOnMount: true, // Refetch when component mounts

    // Network mode
    networkMode: 'online', // Only run queries when online
  },
  mutations: {
    // Retry configuration for mutations
    retry: 0, // Don't retry mutations by default
    networkMode: 'online', // Only run mutations when online
  },
};

/**
 * Create and configure the React Query client
 *
 * This client is used throughout the application for data fetching,
 * caching, and synchronization.
 */
export const queryClient = new QueryClient({
  defaultOptions,
});

/**
 * Query keys for different data types
 *
 * Centralized query key factory to ensure consistency across the app.
 */
export const queryKeys = {
  // User-related queries
  user: {
    all: ['user'] as const,
    profile: () => [...queryKeys.user.all, 'profile'] as const,
    subscription: () => [...queryKeys.user.all, 'subscription'] as const,
  },

  // Project-related queries
  projects: {
    all: ['projects'] as const,
    lists: () => [...queryKeys.projects.all, 'list'] as const,
    list: (filters: Record<string, unknown>) =>
      [...queryKeys.projects.lists(), filters] as const,
    details: () => [...queryKeys.projects.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.projects.details(), id] as const,
  },

  // Photo-related queries
  photos: {
    all: ['photos'] as const,
    lists: () => [...queryKeys.photos.all, 'list'] as const,
    list: (projectId: string) => [...queryKeys.photos.lists(), projectId] as const,
    detail: (id: string) => [...queryKeys.photos.all, 'detail', id] as const,
  },

  // Estimation-related queries
  estimates: {
    all: ['estimates'] as const,
    detail: (projectId: string) => [...queryKeys.estimates.all, projectId] as const,
  },

  // Shopping list queries
  shoppingLists: {
    all: ['shoppingLists'] as const,
    detail: (projectId: string) => [...queryKeys.shoppingLists.all, projectId] as const,
    items: (projectId: string) =>
      [...queryKeys.shoppingLists.all, projectId, 'items'] as const,
  },

  // Pricing queries
  pricing: {
    all: ['pricing'] as const,
    comparison: (itemId: string) => [...queryKeys.pricing.all, 'comparison', itemId] as const,
  },

  // Feedback queries
  feedback: {
    all: ['feedback'] as const,
    list: (projectId: string) => [...queryKeys.feedback.all, 'list', projectId] as const,
  },
};
