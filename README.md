# EstiMate - AI Materials Estimation Platform

AI-powered materials estimation and project planning platform for construction and renovation projects.

## Overview

EstiMate analyzes project photos and specifications to provide accurate materials estimates, pricing, and timelines using computer vision and AI.

## Features

- **Photo Analysis**: Upload project photos for AI-powered material detection
- **Smart Estimation**: Machine learning models for accurate quantity predictions
- **Price Intelligence**: Real-time pricing from multiple suppliers
- **Timeline Generation**: Automated project scheduling
- **Shopping Lists**: Organized materials lists with purchase links
- **Contractor Matching**: Connect with qualified contractors

## Tech Stack

### Backend
- **Python 3.11+** with FastAPI
- **PostgreSQL 15+** for primary database
- **Redis 7+** for caching and sessions
- **SQLAlchemy 2.0** for ORM
- **Pydantic** for validation
- **Google Cloud Vision** for image analysis
- **scikit-learn** for ML models

### Frontend
- **TypeScript 5.x**
- **React 18**
- **Tailwind CSS**
- **React Query** for state management
- **Vite** for build tooling

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Poetry (Python dependency manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/estimate.git
   cd estimate
   ```

2. **Start infrastructure services**
   ```bash
   docker-compose up -d
   ```

3. **Backend setup**
   ```bash
   cd backend
   poetry install
   cp .env.example .env
   # Edit .env with your configuration
   poetry run uvicorn src.main:app --reload
   ```

4. **Frontend setup**
   ```bash
   cd frontend
   npm install
   cp .env.example .env
   # Edit .env with your configuration
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Development

### Running Tests

**Backend:**
```bash
cd backend
poetry run pytest tests/unit/ -v --cov=src
poetry run pytest tests/integration/ -v  # Requires Docker services
poetry run pytest tests/smoke/ -v
```

**Frontend:**
```bash
cd frontend
npm test
```

### Code Quality

**Backend:**
```bash
cd backend
poetry run black .
poetry run ruff check .
poetry run mypy src/
```

**Frontend:**
```bash
cd frontend
npm run lint
npm run format
```

### Pre-commit Hooks

```bash
cd backend
poetry run pre-commit install
poetry run pre-commit run --all-files
```

## Testing with Act (Local CI/CD)

Test GitHub Actions workflows locally before pushing:

```bash
# Test pull request workflow
act pull_request

# Test specific job
act pull_request -j test-backend

# Test push workflow
act push
```

## Project Structure

```
estimate/
├── backend/                 # FastAPI backend
│   ├── src/
│   │   ├── core/           # Configuration, health checks
│   │   ├── api/            # API routes and middleware
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── repositories/   # Data access layer
│   ├── tests/
│   │   ├── unit/           # Unit tests
│   │   ├── integration/    # Integration tests
│   │   └── smoke/          # Smoke tests
│   └── pyproject.toml
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── utils/
│   └── package.json
├── specs/                  # Feature specifications
├── .github/workflows/      # CI/CD workflows
└── docker-compose.yml      # Local development services
```

## Phase 1 Status ✅

**Project Foundation - Complete (100% Test Coverage)**

- [x] Backend project structure
- [x] Configuration management with Pydantic Settings
- [x] Health check endpoints
- [x] Docker Compose infrastructure (PostgreSQL, Redis)
- [x] Comprehensive test suite (45 tests, 100% coverage)
- [x] CI/CD pipeline with GitHub Actions
- [x] Pre-commit hooks and code quality tools

### Test Coverage: 100%
```
Total: 28/28 statements
- Unit Tests: 25 tests
- Smoke Tests: 20 tests
- Integration Tests: 11 tests
```

## Contributing

1. Create a feature branch from `main`
2. Make your changes with tests
3. Ensure all tests pass and coverage is 100%
4. Test locally with `act` before pushing
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For questions or issues, please open a GitHub issue.

---

Built with [Claude Code](https://claude.com/claude-code) using the [Spec Kit](https://github.com/jmanhype/speckit) workflow framework.
