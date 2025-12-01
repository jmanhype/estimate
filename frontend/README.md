# EstiMate Frontend

React-based frontend for EstiMate AI Materials Estimation.

## Tech Stack

- **React 19** - UI library
- **TypeScript 5.9** - Type safety
- **Vite 7** - Build tool & dev server
- **React Router 7** - Client-side routing
- **TanStack Query (React Query)** - Data fetching & caching
- **Axios** - HTTP client
- **Tailwind CSS 4** - Utility-first styling
- **Supabase** - Authentication
- **Stripe** - Payments

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:5173
```

## Development

### Running Development Server

```bash
npm run dev
```

The dev server runs at http://localhost:5173 with hot module replacement.

### Running Tests

```bash
# Run unit tests
npm run test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run E2E tests (Playwright)
npm run test:e2e

# Open Playwright UI
npm run test:e2e:ui
```

### Code Quality

```bash
# Lint code
npm run lint

# Fix linting issues
npm run lint:fix

# Type check
npm run type-check

# Format code
npm run format
```

### Building for Production

```bash
# Build
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── common/         # Reusable UI components
│   │   ├── projects/       # Project-related components
│   │   ├── estimation/     # Photo upload & estimation
│   │   ├── shopping-list/  # Shopping list components
│   │   └── ...
│   ├── hooks/              # Custom React hooks
│   ├── pages/              # Page components (routes)
│   ├── services/           # API clients & services
│   ├── types/              # TypeScript type definitions
│   ├── App.tsx             # Main app component
│   └── main.tsx            # Entry point
├── tests/
│   ├── unit/               # Component & hook tests
│   ├── e2e/                # End-to-end tests
│   └── setup.ts            # Test setup
├── public/                 # Static assets
├── index.html              # HTML template
└── vite.config.ts          # Vite configuration
```

## Environment Variables

Create `.env.local` file:

```env
# API Base URL
VITE_API_BASE_URL=http://localhost:8000/api/v1

# Supabase
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key

# Stripe
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_test_key

# Environment
VITE_ENVIRONMENT=development
```

## Key Features

- **Accessible**: WCAG 2.1 AA compliant
- **Responsive**: Mobile-first design
- **Performant**: Code splitting, lazy loading
- **Type-safe**: Full TypeScript coverage
- **Tested**: Unit & E2E tests with >90% coverage
