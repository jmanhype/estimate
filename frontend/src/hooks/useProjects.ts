/**
 * Custom hooks for project data fetching using React Query
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '../lib/queryClient';

// Placeholder types - will be replaced with actual API types
interface Project {
  id: string;
  title: string;
  description: string;
  status: string;
  created_at: string;
}

interface CreateProjectInput {
  title: string;
  description?: string;
}

/**
 * Fetch all projects for the current user
 */
export function useProjects() {
  return useQuery({
    queryKey: queryKeys.projects.lists(),
    queryFn: async (): Promise<Project[]> => {
      // TODO: Replace with actual API call
      // const response = await apiClient.get('/projects');
      // return response.data;
      return [];
    },
  });
}

/**
 * Fetch a single project by ID
 */
export function useProject(id: string) {
  return useQuery({
    queryKey: queryKeys.projects.detail(id),
    queryFn: async (): Promise<Project> => {
      // TODO: Replace with actual API call
      // const response = await apiClient.get(`/projects/${id}`);
      // return response.data;
      throw new Error('Not implemented');
    },
    enabled: !!id, // Only run if ID is provided
  });
}

/**
 * Create a new project
 */
export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (input: CreateProjectInput): Promise<Project> => {
      // TODO: Replace with actual API call
      // const response = await apiClient.post('/projects', input);
      // return response.data;
      throw new Error('Not implemented');
    },
    onSuccess: () => {
      // Invalidate projects list to trigger refetch
      queryClient.invalidateQueries({
        queryKey: queryKeys.projects.lists(),
      });
    },
  });
}

/**
 * Update an existing project
 */
export function useUpdateProject(id: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (input: Partial<CreateProjectInput>): Promise<Project> => {
      // TODO: Replace with actual API call
      // const response = await apiClient.patch(`/projects/${id}`, input);
      // return response.data;
      throw new Error('Not implemented');
    },
    onSuccess: () => {
      // Invalidate both the project detail and the list
      queryClient.invalidateQueries({
        queryKey: queryKeys.projects.detail(id),
      });
      queryClient.invalidateQueries({
        queryKey: queryKeys.projects.lists(),
      });
    },
  });
}

/**
 * Delete a project
 */
export function useDeleteProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string): Promise<void> => {
      // TODO: Replace with actual API call
      // await apiClient.delete(`/projects/${id}`);
      throw new Error('Not implemented');
    },
    onSuccess: () => {
      // Invalidate projects list to trigger refetch
      queryClient.invalidateQueries({
        queryKey: queryKeys.projects.lists(),
      });
    },
  });
}
