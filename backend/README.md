# EstiMate Backend API

FastAPI-based backend for EstiMate AI Materials Estimation.

## Tech Stack

- **Python 3.11+**
- **FastAPI 0.123+** - Modern async web framework
- **SQLAlchemy 2.0** - ORM with async support
- **PostgreSQL 15** - Primary database
- **Redis 7** - Caching and session storage
- **Alembic** - Database migrations
- **Pytest** - Testing framework

## Quick Start

```bash
# Install dependencies
poetry install

# Start local services (PostgreSQL, Redis)
cd ../shared && docker-compose up -d

# Run database migrations
poetry run alembic upgrade head

# Start development server
poetry run uvicorn src.main:app --reload

# Run tests
poetry run pytest
```

## Project Structure

```
backend/
├── src/                      # Source code
│   ├── api/                  # API routes
│   │   ├── v1/              # API v1 endpoints
│   │   └── middleware/      # Custom middleware
│   ├── core/                # Core configuration
│   ├── models/              # SQLAlchemy models
│   ├── repositories/        # Data access layer
│   ├── schemas/             # Pydantic schemas
│   │   ├── request/         # Request DTOs
│   │   └── response/        # Response DTOs
│   └── services/            # Business logic
│       ├── auth/            # Authentication
│       ├── computer_vision/ # CV integration
│       ├── estimation/      # Material calculations
│       ├── pricing/         # Retailer pricing
│       └── ...
├── tests/                   # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   ├── contract/           # Contract tests
│   └── performance/        # Load tests
├── alembic/                # Database migrations
└── pyproject.toml          # Dependencies & config
```

## Development

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test file
poetry run pytest tests/unit/test_estimation/test_waste_calculator.py

# Run unit tests only
poetry run pytest tests/unit/

# Run integration tests
poetry run pytest tests/integration/
```

### Code Quality

```bash
# Format code
poetry run black src/ tests/

# Lint
poetry run ruff check src/ tests/

# Type check
poetry run mypy src/

# Security scan
poetry run bandit -r src/
```

### Database Migrations

```bash
# Create new migration
poetry run alembic revision --autogenerate -m "Add new field"

# Apply migrations
poetry run alembic upgrade head

# Rollback migration
poetry run alembic downgrade -1
```

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/api/v1/openapi.json

## Environment Variables

See `.env.example` for required environment variables.
