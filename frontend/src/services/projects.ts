/**
 * Projects API service
 *
 * Provides API methods for project CRUD operations.
 */

import { apiClient } from '../lib/apiClient';

/**
 * Project type definitions
 * These should eventually be imported from a shared types package
 */
export interface Project {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  status: 'draft' | 'active' | 'completed' | 'archived';
  created_at: string;
  updated_at: string;
}

export interface CreateProjectInput {
  title: string;
  description?: string;
}

export interface UpdateProjectInput {
  title?: string;
  description?: string;
  status?: 'draft' | 'active' | 'completed' | 'archived';
}

export interface ProjectListResponse {
  projects: Project[];
  total: number;
  page: number;
  per_page: number;
}

/**
 * Projects API service object
 */
export const projectsApi = {
  /**
   * Get all projects for the current user
   */
  async getAll(params?: { page?: number; per_page?: number }): Promise<ProjectListResponse> {
    const response = await apiClient.get<ProjectListResponse>('/projects', { params });
    return response.data;
  },

  /**
   * Get a single project by ID
   */
  async getById(id: string): Promise<Project> {
    const response = await apiClient.get<Project>(`/projects/${id}`);
    return response.data;
  },

  /**
   * Create a new project
   */
  async create(input: CreateProjectInput): Promise<Project> {
    const response = await apiClient.post<Project>('/projects', input);
    return response.data;
  },

  /**
   * Update an existing project
   */
  async update(id: string, input: UpdateProjectInput): Promise<Project> {
    const response = await apiClient.patch<Project>(`/projects/${id}`, input);
    return response.data;
  },

  /**
   * Delete a project
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/projects/${id}`);
  },
};
