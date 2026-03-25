# EstiMate

Materials estimation platform for construction and renovation projects. Intended to analyze project photos and specifications to produce quantity estimates, pricing, and timelines.

**Status:** Phase 1 (project foundation) complete. Backend has health check endpoints, configuration management, and test infrastructure. No estimation logic, image analysis, or pricing features are implemented yet. Phase 2 (database models, repository layer) has not started.

## What Exists

Phase 1 delivered the project skeleton:

- FastAPI backend with health check endpoints (`/health`, `/`)
- Pydantic Settings configuration management
- PostgreSQL 15 + Redis 7 via Docker Compose
- CI/CD pipeline (GitHub Actions, 5 jobs, all passing)
- Multi-stage Dockerfiles for backend and frontend
- React 18 + TypeScript frontend scaffold (no functional pages)
- Pre-commit hooks (Black, Ruff, Mypy, Bandit)
- Playwright E2E test infrastructure

## What Does Not Exist Yet

- Photo upload or analysis (Google Cloud Vision integration is a dependency, not implemented)
- Materials estimation ML models
- Pricing intelligence or supplier integrations
- Timeline generation
- Contractor matching
- User authentication beyond JWT stubs
- Any actual project or estimate data models

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Backend | FastAPI, Python 3.11 | Poetry for dependency management |
| Database | PostgreSQL 15 | No models or migrations beyond scaffold |
| Cache | Redis 7 | Configured, not used by application code |
| Frontend | React 18, TypeScript 5, Vite | Tailwind CSS, React Query |
| Auth | Supabase client configured | Not integrated |
| Image Analysis | google-cloud-vision (dependency) | Not implemented |
| Payments | Stripe (dependency) | Not implemented |
| CI | GitHub Actions | 5 jobs: backend test, frontend test, security scan, E2E, Docker build |
| Infra | Docker Compose | Published images: batmanosama/estimate-backend, estimate-frontend |

## Running Locally

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- Poetry

### Setup

```bash
git clone https://github.com/jmanhype/estimate.git
cd estimate
docker-compose up -d

# Backend
cd backend
poetry install
cp .env.example .env
poetry run uvicorn src.main:app --reload

# Frontend
cd frontend
npm install
cp .env.example .env
npm run dev
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |

## Tests

Phase 1 test suite: 50 tests, 100% coverage of the 41 statements that exist.

| Category | Count | What They Test |
|----------|-------|---------------|
| Unit | 26 | Config loading, health endpoint, main app |
| Smoke | 22 | Project structure validation |
| E2E | 2 | Backend health check via Playwright |
| Integration | 11 | Docker service connectivity (requires running containers) |

```bash
# Unit + smoke (no Docker required)
cd backend && poetry run pytest tests/unit/ tests/smoke/ -v --cov=src

# Integration (requires Docker)
docker-compose up -d
cd backend && poetry run pytest tests/integration/ -v

# Frontend
cd frontend && npm test
```

100% coverage is accurate but misleading -- there are only 41 statements to cover (config, health check, app entrypoint). The number will drop once actual business logic is added.

## Project Structure

```
estimate/
  backend/
    src/
      core/          # config.py (27 statements), health.py (2 statements)
      main.py        # FastAPI app (12 statements)
    tests/
      unit/          # 26 tests
      smoke/         # 22 tests
      integration/   # 11 tests
  frontend/
    src/
      components/    # Button, Card, Input, etc. (scaffolds)
      pages/         # Home, Login, Projects, NotFound (scaffolds)
    tests/
      e2e/           # 2 Playwright tests
  specs/
    001-materials-estimation/   # Spec Kit feature specification
  shared/
    docker-compose.yml
```

## CI/CD

All 5 GitHub Actions jobs pass:

| Job | Duration | What It Does |
|-----|----------|-------------|
| Backend Tests | ~1m | pytest with coverage on Python 3.11 + PostgreSQL 15 + Redis 7 |
| Frontend Tests | ~23s | Vitest, TypeScript type-check, ESLint, build |
| Security Scan | ~15s | Trivy vulnerability scanner, Bandit |
| E2E Tests | ~1m23s | Playwright against running backend |
| Build Docker Images | ~1m51s | Multi-stage builds, push to Docker Hub |

## Planned Features (Not Implemented)

Per the spec in `specs/001-materials-estimation/`:

1. Photo upload and AI-powered material detection
2. Quantity estimation via ML models
3. Supplier price lookups
4. Project timeline generation
5. Shopping list export
6. Contractor matching

None of these are built. The spec exists as a planning artifact.

## License

MIT. See [LICENSE](LICENSE).
