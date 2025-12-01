# EstiMate - AI Materials Estimation

> AI-powered home renovation materials estimation and shopping list generator

[![CI](https://github.com/your-org/estimate/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/estimate/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/your-org/estimate/branch/main/graph/badge.svg)](https://codecov.io/gh/your-org/estimate)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**EstiMate** is a full-stack web application that uses computer vision and AI to estimate materials needed for home renovation projects. Simply upload photos of your space, and EstiMate generates accurate shopping lists with waste calculations and multi-retailer price comparisons.

## Features

- 📸 **Photo-Based Estimation** - Upload room photos for AI-powered material calculations
- 🎨 **Project Templates** - Pre-configured templates for kitchens, bathrooms, bedrooms, and more
- 🧮 **Waste Calculations** - Intelligent waste factors based on material type and skill level
- 🛒 **Shopping Lists** - Organized lists with quantities, units, and waste percentages
- 💰 **Price Comparisons** - Compare prices across Home Depot, Lowe's, and more
- 📊 **Budget Tracking** - Set budgets and track actual vs. estimated costs
- ⏱️ **Timeline Planning** - Phase-based project timelines with material order dates
- 👷 **Contractor Mode** - Professional quotes, branded PDFs, and analytics (Business tier)
- 🔐 **Secure & Compliant** - Row-level security, encryption, and SOC2-ready architecture

## Quick Start

### Prerequisites

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop/)
- **Git** - [Download](https://git-scm.com/downloads)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/estimate.git
cd estimate

# Start local services (PostgreSQL, Redis, Mailhog)
cd shared
docker-compose up -d

# Setup backend
cd ../backend
poetry install
cp .env.example .env
# Edit .env with your API keys (Supabase, Google Cloud Vision, Stripe)
poetry run alembic upgrade head
poetry run uvicorn src.main:app --reload

# Setup frontend (in new terminal)
cd ../frontend
npm install
cp .env.example .env.local
# Edit .env.local with your API keys
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Mailhog UI**: http://localhost:8025

## Project Structure

```
estimate/
├── backend/              # FastAPI backend
│   ├── src/             # Source code
│   ├── tests/           # Test suite (pytest)
│   └── pyproject.toml   # Dependencies
├── frontend/            # React frontend
│   ├── src/             # Source code
│   ├── tests/           # Test suite (vitest, playwright)
│   └── package.json     # Dependencies
├── shared/              # Shared resources
│   ├── docker-compose.yml  # Local services
│   ├── docs/            # Documentation
│   └── scripts/         # Shared scripts
└── specs/               # Feature specifications
    └── 001-materials-estimation/
```

## Tech Stack

### Backend
- **Python 3.11+** with **FastAPI 0.123+**
- **PostgreSQL 15** with Row-Level Security (RLS)
- **Redis 7** for caching
- **SQLAlchemy 2.0** with async support
- **Alembic** for database migrations
- **Google Cloud Vision API** for photo analysis
- **Stripe** for payment processing

### Frontend
- **React 19** with **TypeScript 5.9**
- **Vite 7** for build tooling
- **React Router 7** for routing
- **TanStack Query** for data fetching
- **Tailwind CSS 4** for styling
- **Supabase Auth** for authentication
- **Playwright** for E2E testing

## Development

### Running Tests

```bash
# Backend tests
cd backend
poetry run pytest
poetry run pytest --cov=src --cov-report=html

# Frontend tests
cd frontend
npm run test
npm run test:e2e
```

### Code Quality

```bash
# Backend
poetry run black src/ tests/
poetry run ruff check src/ tests/
poetry run mypy src/
poetry run bandit -r src/

# Frontend
npm run lint
npm run type-check
npm run format
```

### Database Migrations

```bash
# Create migration
poetry run alembic revision --autogenerate -m "Add new field"

# Apply migrations
poetry run alembic upgrade head

# Rollback migration
poetry run alembic downgrade -1
```

## Deployment

See [Deployment Guide](./shared/docs/deployment.md) for production deployment instructions.

### Environment Support

- **Development**: Local with Docker Compose
- **Staging**: Vercel (frontend) + Railway (backend)
- **Production**: Vercel (frontend) + AWS ECS (backend)

## Architecture

EstiMate follows a **microservices-inspired modular monolith** architecture:

- **API Gateway**: FastAPI with versioned REST endpoints
- **Service Layer**: Business logic (estimation, pricing, contractors)
- **Repository Layer**: Data access with RLS enforcement
- **Event-Driven**: Async photo analysis with webhooks
- **Caching Strategy**: Multi-tier caching (Redis, CDN)

See [Architecture Decision Records](./shared/docs/adr/) for detailed design decisions.

## API Documentation

Interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/api/v1/openapi.json

## Subscription Tiers

| Feature | Free | Pro ($9.99/mo) | Business ($49.99/mo) |
|---------|------|----------------|----------------------|
| Projects | 3 | Unlimited | Unlimited |
| Photos/Project | 3 | 20 | 20 |
| Price Comparison | ❌ | ✅ | ✅ |
| Timeline Planning | ❌ | ✅ | ✅ |
| Contractor Quotes | ❌ | ❌ | ✅ |
| Multi-Factor Auth | ❌ | ❌ | ✅ |

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure tests pass (`pytest` and `npm test`)
5. Commit with conventional commits (`feat: Add amazing feature`)
6. Push to your fork
7. Open a Pull Request

## Security

EstiMate implements defense-in-depth security:

- **Authentication**: JWT tokens via Supabase Auth
- **Authorization**: Role-based access control (RBAC)
- **Data Protection**: Encryption at rest and in transit (TLS 1.3)
- **Tenant Isolation**: PostgreSQL Row-Level Security (RLS)
- **Input Validation**: Pydantic schemas with sanitization
- **Rate Limiting**: Tier-based API rate limits

Report security vulnerabilities to security@estimate.com.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## Acknowledgments

- **Google Cloud Vision API** for object detection
- **Supabase** for authentication and storage
- **Stripe** for payment processing
- **FastAPI** and **React** communities

## Support

- **Documentation**: https://docs.estimate.com
- **Community**: https://community.estimate.com
- **Email**: support@estimate.com
- **Twitter**: @EstimateApp

---

**Built with ❤️ by the EstiMate Team**
