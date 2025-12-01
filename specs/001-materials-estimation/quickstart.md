# EstiMate Developer Quickstart

**Last Updated**: 2025-11-30
**Estimated Setup Time**: 30-45 minutes

This guide will help you set up a local development environment for EstiMate.

---

## Prerequisites

Before you begin, ensure you have the following installed:

### Required

- **Python 3.11+**: [Download](https://www.python.org/downloads/)
  ```bash
  python --version  # Should show 3.11 or higher
  ```

- **Node.js 18+**: [Download](https://nodejs.org/)
  ```bash
  node --version  # Should show 18.x or higher
  npm --version
  ```

- **Docker Desktop**: [Download](https://www.docker.com/products/docker-desktop/)
  - Used for PostgreSQL, Redis, and local services
  ```bash
  docker --version
  docker-compose --version
  ```

- **Git**: [Download](https://git-scm.com/downloads)
  ```bash
  git --version
  ```

### Recommended

- **Poetry** (Python package manager): [Install](https://python-poetry.org/docs/#installation)
  ```bash
  curl -sSL https://install.python-poetry.org | python3 -
  poetry --version
  ```

- **VS Code** with extensions:
  - Python (Microsoft)
  - Pylance
  - ESLint
  - Prettier
  - REST Client (for API testing)

---

## Project Structure

```
estimateproject/
├── backend/          # FastAPI application
│   ├── src/          # Source code
│   ├── tests/        # Tests (pytest)
│   ├── alembic/      # Database migrations
│   └── pyproject.toml
├── frontend/         # React application
│   ├── src/          # Source code
│   ├── tests/        # Tests (vitest, playwright)
│   └── package.json
├── shared/
│   ├── docs/         # Shared documentation
│   ├── scripts/      # Development scripts
│   └── docker-compose.yml
└── specs/            # Feature specifications (this repo)
    └── 001-materials-estimation/
```

---

## Step 1: Clone Repository

```bash
# Clone the repository
git clone https://github.com/your-org/estimate.git
cd estimate

# Checkout the feature branch
git checkout 001-materials-estimation
```

---

## Step 2: Environment Setup

### Backend Environment Variables

Create `backend/.env` file:

```bash
# Copy template
cp backend/.env.example backend/.env

# Edit with your values
```

**Required Environment Variables**:

```env
# Database (local PostgreSQL via Docker)
DATABASE_URL=postgresql://estimate:estimate@localhost:5432/estimate_dev

# Redis (local via Docker)
REDIS_URL=redis://localhost:6379/0

# Supabase Auth
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# JWT Secret (for local testing, use Supabase JWT secret)
JWT_SECRET=your-jwt-secret-from-supabase

# Storage (Supabase Storage or S3)
STORAGE_BACKEND=supabase  # or 's3'
SUPABASE_STORAGE_URL=https://your-project.supabase.co/storage/v1
# OR for S3:
# AWS_ACCESS_KEY_ID=your-access-key
# AWS_SECRET_ACCESS_KEY=your-secret-key
# AWS_S3_BUCKET=estimate-dev-photos
# AWS_REGION=us-east-1

# Computer Vision (Google Cloud Vision)
GOOGLE_APPLICATION_CREDENTIALS=./secrets/google-cloud-key.json
# OR for AWS Rekognition:
# AWS_REKOGNITION_REGION=us-east-1

# Stripe (test mode)
STRIPE_SECRET_KEY=sk_test_your_test_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
STRIPE_PRICE_ID_PRO_MONTHLY=price_test_pro_monthly
STRIPE_PRICE_ID_PRO_ANNUAL=price_test_pro_annual
STRIPE_PRICE_ID_BUSINESS_MONTHLY=price_test_business_monthly

# Email (optional for dev)
SMTP_HOST=localhost
SMTP_PORT=1025  # Mailhog
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=noreply@estimate.local

# Development Settings
ENVIRONMENT=development
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend Environment Variables

Create `frontend/.env.local`:

```bash
cp frontend/.env.example frontend/.env.local
```

```env
# API Base URL
VITE_API_BASE_URL=http://localhost:8000/api/v1

# Supabase (frontend)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key

# Stripe (test publishable key)
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_test_key

# Environment
VITE_ENVIRONMENT=development
```

---

## Step 3: Start Local Services (Docker)

Start PostgreSQL, Redis, and Mailhog:

```bash
cd shared
docker-compose up -d

# Verify services are running
docker-compose ps

# Expected output:
# NAME                 STATUS
# postgres            Up
# redis               Up
# mailhog             Up (ports 1025, 8025)
```

**Docker Compose File** (`shared/docker-compose.yml`):
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: estimate
      POSTGRES_PASSWORD: estimate
      POSTGRES_DB: estimate_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  mailhog:
    image: mailhog/mailhog
    ports:
      - "1025:1025"  # SMTP
      - "8025:8025"  # Web UI

volumes:
  postgres_data:
  redis_data:
```

**Access Services**:
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- Mailhog UI: http://localhost:8025 (view sent emails)

---

## Step 4: Setup Backend

### Install Dependencies

```bash
cd backend

# Using Poetry (recommended)
poetry install

# Or using pip
pip install -r requirements.txt
```

### Run Database Migrations

```bash
# Activate virtual environment
poetry shell

# Run Alembic migrations
alembic upgrade head

# Verify tables created
psql postgresql://estimate:estimate@localhost:5432/estimate_dev -c "\dt"
```

**Expected Tables**:
- `user_profiles`
- `subscriptions`
- `projects`
- `project_photos`
- `shopping_lists`
- `shopping_list_items`
- `retailer_prices`

### Seed Database (Optional)

```bash
# Create test data
python scripts/seed_database.py

# Creates:
# - 3 test users (beginner, intermediate, expert)
# - 10 sample projects
# - 100 retailer prices
```

### Run Backend Server

```bash
# Development server with hot reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Server starts at http://localhost:8000
# API docs at http://localhost:8000/docs (Swagger UI)
# OpenAPI schema at http://localhost:8000/api/v1/openapi.json
```

### Run Backend Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_estimation/test_waste_calculator.py

# Run integration tests only
pytest tests/integration/

# View coverage report
open htmlcov/index.html
```

---

## Step 5: Setup Frontend

### Install Dependencies

```bash
cd frontend

# Install packages
npm install

# Or using yarn
yarn install
```

### Run Frontend Server

```bash
# Development server with hot reload
npm run dev

# Server starts at http://localhost:5173
# (Vite default port, may use 5174 if 5173 taken)
```

### Run Frontend Tests

```bash
# Run unit tests (Vitest)
npm run test

# Run tests in watch mode
npm run test:watch

# Run E2E tests (Playwright)
npm run test:e2e

# Open Playwright UI
npm run test:e2e:ui
```

---

## Step 6: Verify Setup

### Test API Endpoints

**Using REST Client** (VS Code extension):

Create `test.http` file:
```http
### Health Check
GET http://localhost:8000/health

### Get Auth Token (replace with your Supabase test user)
@token = your_jwt_token_here

### List Projects
GET http://localhost:8000/api/v1/projects
Authorization: Bearer {{token}}

### Create Project
POST http://localhost:8000/api/v1/projects
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "name": "Test Living Room Repaint",
  "project_type": "painting",
  "budget_amount": 500.00
}
```

**Using cURL**:
```bash
# Health check
curl http://localhost:8000/health

# List projects (replace TOKEN)
curl -H "Authorization: Bearer TOKEN" \
     http://localhost:8000/api/v1/projects
```

### Test Frontend

1. Open http://localhost:5173
2. Click "Sign In" → Create test account via Supabase
3. Create a new project
4. Upload photos (test with any room photo)
5. Generate estimation
6. View shopping list

---

## Step 7: Database Management

### Connect to PostgreSQL

```bash
# Using psql
psql postgresql://estimate:estimate@localhost:5432/estimate_dev

# Common commands
\dt          # List tables
\d projects  # Describe table
\q           # Quit
```

### Using pgAdmin (GUI)

1. Install [pgAdmin](https://www.pgadmin.org/download/)
2. Add server:
   - Host: localhost
   - Port: 5432
   - Database: estimate_dev
   - Username: estimate
   - Password: estimate

### Create New Migration

```bash
cd backend

# Generate migration (after modifying models)
alembic revision --autogenerate -m "Add new field to projects"

# Review generated migration in alembic/versions/

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

---

## Step 8: Debugging

### Backend Debugging (VS Code)

Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "src.main:app",
        "--reload",
        "--port",
        "8000"
      ],
      "jinja": true,
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend"
      }
    }
  ]
}
```

**Set Breakpoints**:
- Click left margin in code editor
- Run "FastAPI" debug configuration (F5)
- Trigger API endpoint → execution pauses at breakpoint

### Frontend Debugging (Chrome DevTools)

1. Open http://localhost:5173
2. Press F12 → Sources tab
3. Set breakpoints in source files (Vite source maps enabled)
4. Trigger user action → execution pauses

### Logging

**Backend** (structured JSON logs):
```python
import logging
logger = logging.getLogger(__name__)

logger.info("Project created", extra={
    "user_id": user.id,
    "project_id": project.id
})
```

**Frontend** (console):
```typescript
console.log('Project created:', project);
```

**View Logs**:
- Backend: Terminal where uvicorn is running
- Frontend: Browser console (F12)

---

## Common Issues & Solutions

### Issue: Database connection refused

**Error**: `connection to server at "localhost" (127.0.0.1), port 5432 failed`

**Solution**:
```bash
# Check if Docker is running
docker ps

# Start Docker services
cd shared
docker-compose up -d postgres

# Verify PostgreSQL is accessible
psql postgresql://estimate:estimate@localhost:5432/estimate_dev -c "SELECT 1"
```

### Issue: Port already in use

**Error**: `Address already in use: bind() failed`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn src.main:app --reload --port 8001
```

### Issue: Module not found (Python)

**Error**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
```bash
# Ensure you're in backend directory
cd backend

# Activate Poetry shell
poetry shell

# Or set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Issue: Supabase Auth errors

**Error**: `Invalid JWT token`

**Solution**:
1. Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY` in `.env`
2. Check JWT secret matches Supabase project settings
3. Test authentication in Supabase dashboard
4. Generate new token via Supabase client

### Issue: Frontend can't connect to API

**Error**: `Network Error` or `CORS error`

**Solution**:
1. Verify backend is running on port 8000
2. Check `VITE_API_BASE_URL=http://localhost:8000/api/v1` in `frontend/.env.local`
3. Verify `CORS_ORIGINS=http://localhost:5173` in `backend/.env`
4. Restart backend after changing CORS settings

---

## Next Steps

After completing quickstart:

1. **Read Architecture Docs**: `shared/docs/adr/`
   - 001-computer-vision-approach.md
   - 002-retailer-api-strategy.md
   - 003-estimation-algorithms.md

2. **Review API Contracts**: `specs/001-materials-estimation/contracts/openapi.yaml`

3. **Run Full Test Suite**:
   ```bash
   # Backend
   cd backend && pytest

   # Frontend
   cd frontend && npm run test && npm run test:e2e
   ```

4. **Start Development**:
   - Pick a task from `specs/001-materials-estimation/tasks.md`
   - Create feature branch: `git checkout -b feature/your-task-name`
   - Write tests first (TDD)
   - Implement feature
   - Run tests: `pytest` (backend) and `npm test` (frontend)
   - Create PR

5. **Join Team Communication**:
   - Slack: #estimate-dev
   - Stand-ups: Daily @ 10am
   - Code reviews: GitHub PRs

---

## Helpful Commands Reference

### Backend

```bash
# Start server
uvicorn src.main:app --reload

# Run tests
pytest
pytest --cov=src --cov-report=html

# Type checking
mypy src/

# Linting
ruff check src/
black src/ --check

# Format code
black src/
ruff check src/ --fix

# Database migrations
alembic upgrade head
alembic downgrade -1
alembic revision --autogenerate -m "description"

# Shell with imports
poetry run python
>>> from src.models import Project
>>> from src.core.database import SessionLocal
```

### Frontend

```bash
# Start dev server
npm run dev

# Run tests
npm run test
npm run test:watch
npm run test:e2e

# Type checking
npm run type-check

# Linting
npm run lint
npm run lint:fix

# Format code
npm run format

# Build for production
npm run build
npm run preview  # Preview build locally
```

### Docker

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f postgres
docker-compose logs -f redis

# Restart service
docker-compose restart postgres

# Remove volumes (fresh start)
docker-compose down -v
```

---

## Getting Help

- **Documentation**: `shared/docs/`
- **API Docs**: http://localhost:8000/docs
- **Team Wiki**: https://wiki.estimate.internal
- **Slack**: #estimate-dev channel
- **Office Hours**: Tuesdays 2-3pm

Happy coding!
