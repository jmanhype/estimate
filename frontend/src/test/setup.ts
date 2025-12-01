/**
 * Test setup and configuration
 *
 * Runs before all tests to set up test environment.
 */

import { beforeAll, vi } from 'vitest';

// Mock Supabase environment variables
beforeAll(() => {
  // Set required Supabase env vars
  import.meta.env.VITE_SUPABASE_URL = 'https://test.supabase.co';
  import.meta.env.VITE_SUPABASE_ANON_KEY = 'test-anon-key';
  import.meta.env.VITE_API_BASE_URL = 'http://localhost:8000/api/v1';
});

// Mock Supabase client
vi.mock('../lib/supabase', () => ({
  supabase: {
    auth: {
      getSession: vi.fn().mockResolvedValue({
        data: { session: null },
        error: null,
      }),
      onAuthStateChange: vi.fn().mockReturnValue({
        data: { subscription: { unsubscribe: vi.fn() } },
      }),
      signInWithPassword: vi.fn(),
      signUp: vi.fn(),
      signOut: vi.fn(),
      resetPasswordForEmail: vi.fn(),
    },
  },
}));
