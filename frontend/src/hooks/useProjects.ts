/**
 * Custom hooks for project data fetching using React Query
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '../lib/queryClient';
import { projectsApi, type Project, type CreateProjectInput, type UpdateProjectInput } from '../services';

/**
 * Fetch all projects for the current user
 */
export function useProjects() {
  return useQuery({
    queryKey: queryKeys.projects.lists(),
    queryFn: async () => {
      const response = await projectsApi.getAll();
      return response.projects;
    },
  });
}

/**
 * Fetch a single project by ID
 */
export function useProject(id: string) {
  return useQuery({
    queryKey: queryKeys.projects.detail(id),
    queryFn: () => projectsApi.getById(id),
    enabled: !!id, // Only run if ID is provided
  });
}

/**
 * Create a new project
 */
export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: CreateProjectInput) => projectsApi.create(input),
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
    mutationFn: (input: UpdateProjectInput) => projectsApi.update(id, input),
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
    mutationFn: (id: string) => projectsApi.delete(id),
    onSuccess: () => {
      // Invalidate projects list to trigger refetch
      queryClient.invalidateQueries({
        queryKey: queryKeys.projects.lists(),
      });
    },
  });
}
