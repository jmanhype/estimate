/**
 * React Router configuration
 */

import { createBrowserRouter, Navigate } from 'react-router-dom';
import { HomePage, ProjectsPage, LoginPage, NotFoundPage } from './pages';

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
    element: <ProjectsPage />,
  },
  {
    path: '/projects/new',
    element: <div>New Project Page (TODO)</div>,
  },
  {
    path: '/projects/:id',
    element: <div>Project Detail Page (TODO)</div>,
  },
  {
    path: '/projects/:id/estimate',
    element: <div>Estimate Page (TODO)</div>,
  },
  {
    path: '/projects/:id/shopping-list',
    element: <div>Shopping List Page (TODO)</div>,
  },
  {
    path: '/subscription',
    element: <div>Subscription Page (TODO)</div>,
  },
  {
    path: '/profile',
    element: <div>Profile Page (TODO)</div>,
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
