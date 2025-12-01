import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from './App';

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />);
    // Should render the home page by default
    expect(screen.getByText(/EstiMate/i)).toBeInTheDocument();
  });

  it('renders home page with call-to-action buttons', () => {
    render(<App />);
    expect(screen.getByText(/Start New Project/i)).toBeInTheDocument();
    expect(screen.getByText(/View Projects/i)).toBeInTheDocument();
  });
});
