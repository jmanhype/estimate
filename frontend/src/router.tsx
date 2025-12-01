/**
 * React Router configuration
 */

import { createBrowserRouter, Navigate } from 'react-router-dom';
import { HomePage, ProjectsPage, LoginPage, NotFoundPage } from './pages';
import { ProtectedRoute } from './components/common/ProtectedRoute';

/**
 * Application router with all route definitions
 */
export const router = createBrowserRouter([
  {
    path: '/',
    element: <HomePage />,
  },
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/projects',
    element: (
      <ProtectedRoute>
        <ProjectsPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/projects/new',
    element: (
      <ProtectedRoute>
        <div>New Project Page (TODO)</div>
      </ProtectedRoute>
    ),
  },
  {
    path: '/projects/:id',
    element: (
      <ProtectedRoute>
        <div>Project Detail Page (TODO)</div>
      </ProtectedRoute>
    ),
  },
  {
    path: '/projects/:id/estimate',
    element: (
      <ProtectedRoute>
        <div>Estimate Page (TODO)</div>
      </ProtectedRoute>
    ),
  },
  {
    path: '/projects/:id/shopping-list',
    element: (
      <ProtectedRoute>
        <div>Shopping List Page (TODO)</div>
      </ProtectedRoute>
    ),
  },
  {
    path: '/subscription',
    element: (
      <ProtectedRoute>
        <div>Subscription Page (TODO)</div>
      </ProtectedRoute>
    ),
  },
  {
    path: '/profile',
    element: (
      <ProtectedRoute>
        <div>Profile Page (TODO)</div>
      </ProtectedRoute>
    ),
  },
  {
    path: '/404',
    element: <NotFoundPage />,
  },
  {
    path: '*',
    element: <Navigate to="/404" replace />,
  },
]);
