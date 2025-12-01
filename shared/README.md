# Shared Resources

Shared resources and services for EstiMate project.

## Docker Compose Services

This directory contains the `docker-compose.yml` file for local development services.

### Services Included

1. **PostgreSQL 15** - Primary database
   - Port: 5432
   - Database: estimate_dev
   - Username: estimate
   - Password: estimate

2. **Redis 7** - Caching and session storage
   - Port: 6379
   - Persistence: appendonly mode

3. **Mailhog** - Email testing
   - SMTP Port: 1025
   - Web UI: http://localhost:8025

### Usage

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart a specific service
docker-compose restart postgres

# Remove all data (fresh start)
docker-compose down -v
```

### Health Checks

All services include health checks to ensure they're ready before use:

```bash
# Check service health
docker-compose ps

# Expected output shows all services as "healthy"
```

### Connecting to Services

#### PostgreSQL
```bash
# Using psql
psql postgresql://estimate:estimate@localhost:5432/estimate_dev

# Using connection string
DATABASE_URL=postgresql://estimate:estimate@localhost:5432/estimate_dev
```

#### Redis
```bash
# Using redis-cli
redis-cli -h localhost -p 6379

# Test connection
redis-cli ping  # Should return PONG
```

#### Mailhog
- Web UI: http://localhost:8025
- SMTP: localhost:1025

## Directory Structure

```
shared/
├── docker-compose.yml       # Local development services
├── docs/                    # Shared documentation
├── scripts/                 # Shared scripts
└── monitoring/              # Monitoring configs
    └── grafana/            # Grafana dashboards
```
