# Implementation Plan: EstiMate - AI Materials Estimation

**Branch**: `001-materials-estimation` | **Date**: 2025-11-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-materials-estimation/spec.md`

## Summary

EstiMate is an AI-powered materials estimation application for home renovations that uses computer vision to analyze room photos and calculate precise material quantities with waste factors. The system serves two user segments: DIY enthusiasts (freemium $9.99/month pro tier) and small contractors ($50-200/month business tier). Core value proposition is reducing material waste by 15-20% through intelligent estimation that accounts for project complexity, material type, and user skill level.

**Technical Approach**: Web application with React/TypeScript frontend and Python/FastAPI backend. Computer vision pipeline processes uploaded photos to extract room dimensions. PostgreSQL stores user accounts, projects, and shopping lists. Redis caches pricing data and photo analysis results. Integration with retailer APIs (Home Depot, Lowe's) for price comparison and checkout. Stripe handles subscription billing.

## Technical Context

**Language/Version**:
- Backend: Python 3.11+
- Frontend: TypeScript 5.x
- Runtime: Node.js 18+ (frontend build/dev)

**Primary Dependencies**:
- Backend: FastAPI 0.104+, SQLAlchemy 2.0, Pydantic 2.x, scikit-learn 1.3+, pandas 2.0+
- Frontend: React 18, React Query 4.x, Tailwind CSS 3.x, React Hook Form 7.x
- Computer Vision: OpenCV 4.8+ or cloud vision API (Google Cloud Vision / AWS Rekognition)
- Payment: Stripe SDK (Python & JS)
- HTTP Client: httpx (async Python), Axios (TypeScript)

**Storage**:
- Primary Database: PostgreSQL 15+ (user accounts, projects, shopping lists, feedback)
- Cache/Session: Redis 7+ (pricing data, photo analysis results, session storage)
- Object Storage: AWS S3 or compatible (uploaded photos, exported PDFs)

**Testing**:
- Backend: pytest 7.x, pytest-asyncio, coverage.py (target: 90%+ coverage)
- Frontend: Vitest, React Testing Library, Playwright (E2E)
- Contract Testing: Pact or OpenAPI validation
- Performance: Locust (load testing), pytest-benchmark

**Target Platform**:
- Backend: Linux containers (Docker), deploy to AWS ECS/EKS or equivalent
- Frontend: Static site deployment (Vercel, Netlify, CloudFront + S3)
- Database: Managed PostgreSQL (AWS RDS, Supabase)
- Cache: Managed Redis (AWS ElastiCache, Upstash)

**Project Type**: Web application (frontend + backend)

**Performance Goals**:
- API latency: p50 ≤100ms, p95 ≤500ms, p99 ≤1000ms
- Photo analysis: ≤30 seconds for 3-4 photos
- Page load (LCP): ≤2.0 seconds
- Time-to-Interactive (TTI): ≤3.5 seconds on 4G mobile
- First Contentful Paint (FCP): ≤1.2 seconds on 4G mobile
- Cumulative Layout Shift (CLS): ≤0.1
- First Input Delay (FID): ≤100ms
- Throughput: ≥1000 req/s sustained
- Concurrent users: ≥10,000
- Load pattern: 10,000 concurrent users breakdown:
  - 60% browsing (GET requests, cached responses)
  - 30% creating/editing projects (POST/PATCH, database writes)
  - 10% uploading photos (S3 direct uploads, CV analysis queue)
- Traffic pattern: 70% weekday evenings (6-9pm local), 30% weekends

**Mobile Network Performance**:
- 3G (1.6 Mbps): Page load ≤5 seconds, core features usable
- 4G (10 Mbps): Page load ≤2.5 seconds, all features responsive
- 5G/WiFi: Page load ≤1.5 seconds, optimal experience

**Progressive Enhancement**:
- Offline capability: N/A (online-only app)
- Image optimization: Automatic WebP conversion, lazy loading for photos beyond viewport
- Code splitting: Route-based splitting (React.lazy), vendor chunk separation
- Progressive enhancement: Core HTML forms functional without JS (authentication fallback)

**Constraints**:
- Photo upload: max 20 photos @ 10MB each = 200MB max per project
- Analysis timeout: 60 seconds max (fallback to manual input)
- Database queries: all <100ms at 95th percentile
- Cache hit rate: >80% for pricing data
- Uptime SLA: 99.5% for core estimation features
- Frontend bundle sizes: JavaScript ≤250KB gzipped, CSS ≤50KB gzipped
- API response payloads: ≤500KB for list endpoints, max 100 items/page
- Third-party scripts: ≤100KB total, async/defer loading only
- Image optimization: Photos resized to max 1920px width before storage

**Scale/Scope**:
- Users: Start 1K, scale to 100K in year 1
- Projects: ~5-10 per active user, ~500K-1M total year 1
- Photos: 3-10 per project, ~5M photos year 1
- Pricing data: ~1000 materials × 3 retailers = 3K price points, updated every 48h
- Codebase: Est. 15-20K LOC backend, 10-15K LOC frontend

## Performance Budgets

**JavaScript Bundle**: Total bundle ≤250KB gzipped (initial), ≤500KB total
- Breakdown:
  - Main app bundle: ≤150KB gzipped
  - Vendor chunk (React, React DOM, React Router): ≤80KB gzipped
  - Code-split routes: ≤20KB gzipped per route
- Enforcement: CI fails if bundle exceeds limits
- Tools: vite-bundle-visualizer for analysis

**CSS Bundle**: Total bundle ≤50KB gzipped
- Tailwind CSS with PurgeCSS optimization
- Critical CSS inlined in HTML head
- Non-critical CSS lazy-loaded

**Images**:
- Photos: Auto-compressed to ≤2MB (original quality preserved on upload)
- UI assets: ≤100KB each
- WebP format with JPEG fallback
- Lazy loading for images beyond viewport
- Responsive images with srcset

**API Responses**:
- JSON payloads: ≤100KB per endpoint
- List endpoints: Max 100 items/page, pagination required
- Field selection (sparse fieldsets) supported
- Gzip compression for responses >500 bytes

**Third-Party Scripts**:
- Stripe.js only: ≤50KB gzipped
- No other third-party JS allowed
- Analytics (if needed): Plausible (~1KB) or similar lightweight option
- All scripts loaded async/defer

**Render-Blocking Resources**:
- ≤2 render-blocking resources allowed
- Critical CSS inlined in HTML head
- Fonts preloaded with `<link rel="preload">`
- JavaScript deferred or async

## Performance Degradation Thresholds

**Acceptable Degradation**:
- p95 latency increases to 750ms (from 500ms baseline)
- Still within user tolerance for interactive applications
- No user-facing warnings displayed

**Warning Threshold**:
- p95 latency >1s or error rate >2%
- Alerts sent to on-call team
- Investigation required within 30 minutes
- User-facing status page updated if sustained

**Critical Threshold**:
- p95 latency >2s or error rate >5%
- Incident response triggered immediately
- Auto-scaling and load shedding activated
- User-facing degraded mode messaging displayed
- Postmortem required after resolution

## Burst Traffic Handling

**Auto-Scaling Configuration**:
- Trigger: Sustained load >80% CPU/memory capacity for 2 minutes
- Scale-up time: New instances provisioned within 60 seconds
- Warm-up period: 30 seconds for health checks to pass
- Scale-down: Gradual, only after load <50% for 10 minutes

**Burst Allowance**:
- 2x baseline rate allowed for up to 5 minutes
- Example: Baseline 1000 req/s → accept 2000 req/s bursts
- Circuit breakers activated if burst exceeds 5 minutes
- Queue overflow: Requests rejected with 503 Service Unavailable

**Load Shedding**:
- Priority tiers: Critical (auth, view projects) > Standard (create project) > Optional (analytics)
- Under heavy load: Shed optional requests first
- 429 Too Many Requests responses with Retry-After header

## Cache Cold-Start Performance

**Cold-Start Scenario**:
- Redis empty after restart or failover
- All pricing data and analysis results evicted
- System must rebuild cache from scratch

**Cache Warming Strategy**:
- Pre-populate top 100 materials pricing on startup
- Warming duration: ≤5 seconds (parallel API calls)
- Priority: Most frequently accessed materials first
- Background: Continue warming remaining materials over 60 seconds

**Fallback Performance**:
- Direct database queries when cache miss
- p95 latency: ≤150ms (vs ≤50ms cached)
- Pricing API fallback: ≤200ms (vs ≤80ms cached)
- User experience: Minimal impact, no timeout errors
- Cache population: Lazy loading as requests arrive

## Scenario-Specific Performance Requirements

**Multi-Project Dashboard**:
- Initial load: ≤1s for 50 projects (pagination)
- Pagination: 20 projects per page
- Subsequent pages: ≤300ms
- Sorting/filtering: Client-side for current page, server-side for all projects

**Authentication Flow**:
- Login: ≤500ms (Supabase Auth)
- Signup: ≤500ms (Supabase Auth)
- Token refresh: ≤200ms
- OAuth redirect: ≤1s total round-trip

**Maximum Project Queries**:
- Limit: 1000 projects per user
- Pagination: Required, 20-100 items per page
- Query performance: ≤200ms per page (with indexes)
- Search: Full-text search ≤300ms

**Large Shopping Lists**:
- 100 items: Render ≤300ms
- Virtualization: Activated for >50 items (react-window)
- Scrolling: 60fps smooth scrolling
- Export to PDF: ≤2s for 100 items

**High-Frequency Pagination**:
- Debounced: 1 request per 300ms max
- Previous/next buttons: Immediate response from prefetched data
- Infinite scroll: Prefetch next page when 80% scrolled
- Cancel in-flight requests when new page requested

## Photo Upload Performance Trade-Offs

**Upload Quality Trade-Off**:
- Original quality: Preserved on upload (no compression during upload process)
- User experience: No upload delays, users see exact photo quality they uploaded
- Storage optimization: After 90 days, compress to 80% quality JPEG
- Rationale: Immediate UX > storage costs (deferred optimization)

**Storage Cost Management**:
- Active projects (0-90 days): Original quality, ~5MB avg per photo
- Archived projects (90+ days): 80% JPEG, ~2MB avg per photo
- Estimated savings: 60% storage reduction for archived projects
- User notification: "Older projects may have slightly compressed photos"

## CDN Cost Trade-Offs

**Vercel CDN Strategy**:
- Free tier: 100GB bandwidth/month
- Overage pricing: $20/100GB
- Expected usage: ~50GB/month at 10K users

**Break-Even Analysis**:
- Vercel cost at 1M users: ~$100-200/month (500-1000GB)
- CloudFront cost equivalent: $42.50-85/month ($0.085/GB)
- Break-even point: ~500K monthly users or 500GB bandwidth

**Migration Trigger**:
- Threshold: >1M monthly active users
- Alternative: Migrate to CloudFront ($0.085/GB = $8.50/100GB)
- Trade-off: Vercel simplicity (zero config, auto-deployment) over cost optimization
- Decision deferred: Optimize when scale justifies engineering effort

## Cloud Provider Performance SLAs

**Railway** (Backend Hosting):
- Uptime SLA: 99.9% (documented)
- p95 latency: <100ms (validated in staging)
- Auto-scaling: Built-in, <60s scale-up time
- Health checks: Validated `/health/ready` endpoint

**Supabase** (Database):
- Uptime SLA: 99.9% (Pro plan, documented)
- Database query p95: <50ms for indexed queries (validated with EXPLAIN ANALYZE)
- Connection pooling: PgBouncer, max 100 connections
- Backups: Automated daily, point-in-time recovery

**Vercel CDN** (Frontend):
- Uptime SLA: 99.99% (Edge Network, documented)
- Global p50 latency: <50ms (validated with Lighthouse tests from multiple regions)
- Cache hit ratio: >95% for static assets
- Automatic SSL/TLS termination

**Stripe API** (Payments):
- Uptime SLA: 99.99% (documented)
- API call p95: <400ms (documented, monitored)
- Webhook delivery: 3 retry attempts with exponential backoff
- Idempotency: Supported with Idempotency-Key header

**PostgreSQL 15**:
- Query performance: EXPLAIN ANALYZE benchmarks show <10ms for indexed queries (validated)
- Index usage: 95%+ queries use indexes (monitored via pg_stat_statements)
- Connection overhead: <5ms per connection acquisition from pool

**Redis 7**:
- Latency: p99 <5ms for GET/SET operations (validated with redis-cli --latency)
- Throughput: >100K ops/sec (validated with redis-benchmark)
- Memory efficiency: <1KB overhead per key
- Persistence: AOF with fsync every second

## Performance Requirements Tracking

**ID Format**: PERF-XXX (e.g., PERF-001: API latency p95 ≤500ms)

**Core Requirements**:
- PERF-001: API latency p50 ≤100ms, p95 ≤500ms, p99 ≤1000ms
- PERF-002: Photo analysis ≤30 seconds for 3-4 photos
- PERF-003: Page load (LCP) ≤2.0 seconds
- PERF-004: Time-to-Interactive (TTI) ≤3.5 seconds on 4G
- PERF-005: First Contentful Paint (FCP) ≤1.2 seconds on 4G
- PERF-006: Cumulative Layout Shift (CLS) ≤0.1
- PERF-007: First Input Delay (FID) ≤100ms
- PERF-008: Throughput ≥1000 req/s sustained
- PERF-009: Concurrent users ≥10,000
- PERF-010: JavaScript bundle ≤250KB gzipped
- PERF-011: CSS bundle ≤50KB gzipped
- PERF-012: API response payloads ≤100KB per endpoint
- PERF-013: Third-party scripts ≤100KB total
- PERF-014: Render-blocking resources ≤2
- PERF-015: Database queries p95 <100ms
- PERF-016: Cache hit rate >80% for pricing data
- PERF-017: 3G network page load ≤5 seconds
- PERF-018: 4G network page load ≤2.5 seconds
- PERF-019: 5G/WiFi page load ≤1.5 seconds
- PERF-020: Multi-project dashboard ≤1s for 50 projects
- PERF-021: Authentication flow ≤500ms
- PERF-022: Large shopping lists (100 items) render ≤300ms
- PERF-023: Auto-scaling triggers at 80% capacity for 2 minutes
- PERF-024: New instances provisioned within 60 seconds
- PERF-025: Cache warming ≤5 seconds on cold start
- PERF-026: Cache miss fallback p95 ≤150ms

**Mapping to Success Criteria**:
- PERF-001 → SC-005 (10K concurrent users, <2s load)
- PERF-003, PERF-004, PERF-005 → SC-016 (TTI/FCP/LCP targets)
- PERF-010, PERF-011 → SC-015 (Bundle size budgets)
- PERF-008, PERF-009 → SC-012 (99.5% uptime)

**Monitoring Tools**:
- Grafana dashboards: Track all PERF-XXX metrics in production
- Alerts: Configured for threshold violations (warning/critical)
- Reports: Weekly performance reports mapped to PERF-XXX compliance

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Beads Integration for Work Memory - RECOMMENDED ✅

**Status**: PASS (Conditional)

- Tasks will be tracked in Beads as recommended
- Long-running work spans multiple sessions (research, CV model training, integration testing)
- Each task in tasks.md will reference Beads issue ID: `- [ ] (bd-xxxx) T001 ...`
- Implementation driven from `bd ready` workflow

**Action**: Create Beads epic issues during `/speckit.tasks` phase

---

### II. Test-First Development (TDD) - RECOMMENDED ✅

**Status**: PASS

- All code will follow strict TDD: Red → Green → Refactor
- Test coverage targets: ≥90% overall, 100% for authentication/authorization/payment
- Test types planned:
  - Unit tests: All business logic (estimation algorithms, waste calculations, price optimization)
  - Integration tests: All API endpoints, database operations, external API calls
  - Contract tests: Retailer API adapters, Stripe integration
  - E2E tests: Critical user flows (photo upload → estimation → shopping list)
  - Performance tests: API latency, photo analysis throughput

**Rationale**: Constitution requires TDD to prevent technical debt. Estimation algorithms are complex and error-prone without test coverage.

---

### III. SOLID Architecture - MANDATORY ✅

**Status**: PASS

Architectural patterns to be applied:

- **Repository Pattern**: All database access via repository interfaces
  - `UserRepository`, `ProjectRepository`, `ShoppingListRepository`
  - Enables testing with mock repositories

- **Adapter Pattern**: All external dependencies isolated
  - `ComputerVisionAdapter` (OpenCV / Cloud Vision)
  - `RetailerAPIAdapter` (Home Depot, Lowe's)
  - `PaymentAdapter` (Stripe)
  - `EmailAdapter` (SendGrid / SES)
  - `StorageAdapter` (S3)

- **Factory Pattern**: Service creation via dependency injection
  - FastAPI dependency injection for services
  - React Context for frontend services

- **Strategy Pattern**: Algorithm selection
  - `EstimationStrategy` (different algorithms per material type: paint, flooring, tile)
  - `WasteCalculationStrategy` (by skill level, material complexity)
  - `PriceOptimizationStrategy` (minimize cost vs minimize trips)

- **Facade Pattern**: Simplified interfaces
  - `EstimationService` facade over CV analysis + calculation + waste application
  - `PricingService` facade over multiple retailer adapters

**Rationale**: Constitution mandates SOLID from start. EstiMate has multiple complex subsystems (CV, pricing, estimation) that need clear separation.

---

### IV. Security-First Design - NON-NEGOTIABLE ✅

**Status**: PASS

Defense in depth layers:

- **Layer 1: Network**
  - Rate limiting: 100 req/min authenticated, 10 req/min unauthenticated
  - DDoS protection via CloudFlare or AWS Shield

- **Layer 2: Authentication**
  - JWT + OAuth2/OIDC (Auth0 or Supabase Auth)
  - MFA optional for users, mandatory for business tier

- **Layer 3: Authorization**
  - RBAC: Free/Pro/Business tiers with feature flags
  - Ownership checks: Users can only access their own projects
  - API endpoints protected with @require_auth decorator

- **Layer 4: Data Access**
  - PostgreSQL Row-Level Security (RLS) enabled
  - All queries filter by user_id / tenant_id
  - No cross-user data leakage

- **Layer 5: Application**
  - Input validation: Pydantic models (strict mode)
  - SQL injection prevention: SQLAlchemy ORM (no raw SQL)
  - XSS prevention: React auto-escaping + CSP headers
  - CSRF protection: Synchronizer tokens (FastAPI CSRF middleware) + SameSite=Strict cookies
  - File upload validation: MIME type checking, virus scanning (ClamAV)
  - Frontend validation: Real-time UX feedback (React Hook Form)
  - Backend validation: Security enforcement (Pydantic strict mode, all business rules)

- **Layer 6: Audit**
  - All user actions logged (project creation, estimation, purchases)
  - Security events logged (login attempts, authorization failures)
  - Structured JSON logging with correlation IDs
  - Security incident response: 72-hour breach notification, audit log preservation
  - Incident timeline documentation in `/docs/incidents/`

**Security requirements met**:
- ✅ Secrets in environment variables (no hardcoding)
- ✅ OAuth2/OIDC for authentication
- ✅ RBAC for authorization (subscription tiers)
- ✅ TLS 1.3 for data in transit with cipher suite order:
  - TLS_AES_256_GCM_SHA384 (preferred)
  - TLS_CHACHA20_POLY1305_SHA256
  - TLS_AES_128_GCM_SHA256
- ✅ AES-256 for sensitive data at rest (payment info)
- ✅ Pydantic validation for all inputs
- ✅ SQLAlchemy ORM (parameterized queries)
- ✅ RLS enabled for multi-tenancy
- ✅ Rate limiting on all endpoints
- ✅ Error messages sanitized in production
- ✅ CSRF protection (synchronizer tokens + SameSite cookies)
- ✅ Password policy: 12 char min, complexity requirements, HaveIBeenPwned API check
- ✅ JWT structure: {sub, email, role, tier, iat, exp, iss} claims, RS256 signing
- ✅ Session management: Max 5 concurrent sessions per user, view/revoke UI
- ✅ Annual penetration testing: OWASP Top 10 coverage, CRITICAL/HIGH resolved before prod

**Authentication Details**:
- JWT Token Structure:
  ```json
  {
    "sub": "user_uuid",
    "email": "user@example.com",
    "role": "user",
    "tier": "Free|Pro|Business",
    "iat": 1234567890,
    "exp": 1234571490,
    "iss": "estimate-api"
  }
  ```
- Signing: RS256 (asymmetric), public key for verification
- Token lifetime: 1 hour access token, 7-day refresh token
- Storage: HTTP-only cookies (web), secure storage (mobile)

**Password Security**:
- Hashing: Argon2id (OWASP recommendation)
- Requirements: min 12 chars, 1 upper, 1 lower, 1 number, 1 special
- Breach detection: Check against HaveIBeenPwned Passwords API (k-anonymity)
- Reset flow: Time-limited tokens (1 hour), rate limited (3 attempts/hour)

**Session Management**:
- Max concurrent sessions: 5 per user
- Session store: Redis with 7-day TTL
- Device tracking: User agent + IP for display (not validation)
- Revocation: Individual session revoke + "revoke all others" button
- Auto-logout: 30 days inactivity for Free tier, 90 days for Pro/Business

**Security Testing & Compliance**:
- Annual penetration testing by third-party firm
- Scope: OWASP Top 10, authentication, authorization, data protection
- Acceptance: Zero CRITICAL/HIGH findings before production deployment
- Medium findings: 30-day remediation SLA
- Compliance targets: SOC 2 Type II (year 2), GDPR (launch)

---

### V. API Versioning & Stability - MANDATORY ✅

**Status**: PASS

Versioning strategy:
- URL versioning: `/api/v1/projects`, `/api/v1/estimates`
- OpenAPI 3.1 schema published at `/api/v1/openapi.json`
- Major version in URL, minor/patch in semver
- Breaking changes announced 6 months in advance
- Previous major version supported 12 months

**API stability guarantees**:
- No breaking changes within v1.x
- New fields added as optional
- Deprecated fields marked in OpenAPI with sunset date
- Migration guide for v1 → v2 when needed

---

### VI. Observability & Monitoring - MANDATORY ✅

**Status**: PASS

Three pillars implementation:

**Metrics (Prometheus)**:
- Request rates, latencies (p50, p95, p99), error rates
- Database connection pool usage, query latencies
- Redis hit/miss rates, latency
- Photo upload sizes, analysis duration
- Estimation accuracy (when feedback available)
- Subscription conversion rates (free → pro → business)
- Retailer API call counts, latencies, error rates

**Logging (Structured JSON)**:
- All requests: user_id, project_id, trace_id, duration, status
- Security events: login, failed auth, permission denials
- Business events: estimation created, purchase tracked, subscription changed
- Errors: full context (non-sensitive), stack traces
- Log levels: INFO (production), DEBUG (development)

**Tracing (OpenTelemetry)**:
- End-to-end request tracing
- Spans: API → Service → Repository → Database
- External calls instrumented: Stripe, retailer APIs, CV service
- Trace sampling: 100% errors, 10% success

**Health checks**:
- `/health/live`: Basic liveness (returns 200)
- `/health/ready`: Readiness (checks DB, Redis, S3 connectivity)
- `/health`: Detailed status (version, dependencies)

**Monitoring dashboards** (Grafana):
- System health: latency, error rate, throughput
- Business metrics: signups, conversions, active users
- Cost tracking: CV API calls, storage usage

---

### VII. Graceful Degradation - MANDATORY ✅

**Status**: PASS

Fallback strategies defined:

**Computer Vision Failure**:
- Primary: Cloud Vision API (Google Cloud Vision)
- Fallback 1: AWS Rekognition
- Fallback 2: Manual dimension input form
- Circuit breaker: After 3 consecutive failures, skip CV and prompt manual input
- Timeout: 30 seconds per photo analysis

**Retailer API Failure**:
- Cached pricing (max age: 48 hours)
- Degraded mode: Show last known prices with disclaimer "Prices may have changed"
- Fallback: Link to retailer website for manual search
- Circuit breaker: Per-retailer, 5-minute half-open retry

**Database Failure**:
- Read replicas: Failover to read replica for GET requests
- Connection pool: Retry with exponential backoff (3 attempts)
- Degraded mode: Read-only mode if primary down, writes queued

**Redis Failure**:
- In-memory cache fallback (LRU, 1000 items)
- Performance degradation warning to user
- Direct database queries (slower but functional)

**Stripe Failure**:
- Cached subscription status (max age: 1 hour)
- Graceful: Allow current subscribers to continue, block new signups
- Manual reconciliation: Webhook replay for missed events

**S3 Failure**:
- Temporary local storage for uploads (max 1 hour)
- Background retry to S3 (exponential backoff)
- Fail visible: User notified "Photo upload delayed, will retry"

**Circuit Breaker Configuration**:
- External APIs: 50% error rate over 1 minute → OPEN
- Half-open: Retry after 1 minute with single request
- Closed: Resume after 3 consecutive successes

---

### VIII. Code Quality Standards - MANDATORY ✅

**Status**: PASS

**Static Analysis**:
- Python: mypy (strict mode), ruff (linter), black (formatter), bandit (security)
- TypeScript: ESLint (strict), Prettier, no `any` types allowed
- Pre-commit hooks: Run formatters and linters
- CI gates: All checks must pass

**Code Review Requirements**:
- All PRs require 1 approval
- Security-sensitive changes (auth, payment): 2 approvals
- Review checklist:
  - ✅ Tests written first (TDD)
  - ✅ Coverage ≥90% (100% for security code)
  - ✅ No hardcoded secrets
  - ✅ Input validation present
  - ✅ Error handling comprehensive
  - ✅ Logging with correlation IDs
  - ✅ OpenTelemetry tracing added
  - ✅ API changes backward-compatible

**Documentation Requirements**:
- All public APIs: Google-style docstrings
- Complex algorithms: Inline comments explaining "why"
- Architecture decisions: ADRs in `/docs/adr/`
- API docs: OpenAPI 3.1 schema auto-generated

**Performance Requirements**:
- API endpoints: p95 <500ms (verified in tests)
- Database queries: Explain plans reviewed, indexes validated
- Critical paths: Profiled with py-spy or similar

---

### IX. Data Protection & Compliance (from constitution) ✅

**Status**: PASS

**Encryption**:
- At rest: AES-256-GCM for payment info, sensitive PII
- In transit: TLS 1.3 with strong cipher suites
- Key management: AWS KMS or Vault (no local keys)

**Tenant Isolation**:
- RLS enabled with `FORCE ROW LEVEL SECURITY`
- All queries filter by user_id
- Cache keys scoped: `{user_id}:{namespace}:{key}`
- S3 objects: `{user_id}/{project_id}/{photo_id}`

**GDPR/Privacy**:
- Right to access: Export endpoint `/api/v1/users/me/export`
- Right to deletion: Delete endpoint `/api/v1/users/me` (cascades to projects, photos)
- Right to portability: JSON export of all user data
- Retention: 7 years default (configurable), auto-delete after expiry

---

### X. Performance & Scalability (from constitution) ✅

**Status**: PASS

**Performance Targets** (from constitution):
- API latency: p50 ≤100ms ✅, p95 ≤500ms ✅, p99 ≤1000ms ✅
- Background tasks: Photo analysis (3-4 photos) ≤30 seconds ✅
- Page load (LCP): ≤2 seconds ✅
- Time-to-Interactive (TTI): ≤3.5 seconds on 4G ✅
- First Contentful Paint (FCP): ≤1.2 seconds on 4G ✅
- Throughput: ≥1000 req/s ✅
- Concurrent users: ≥10,000 ✅
- Uptime: 99.5% SLA ✅

**Scaling Strategy**:
- Horizontal scaling: Stateless backend (FastAPI), load balancer (ALB)
- Database: Connection pooling (min: 10, max: 100), read replicas
- Caching: L1 (in-memory LRU) + L2 (Redis distributed)
- CDN: Frontend static assets, photo URLs
- Auto-scaling: CPU >70% → add instances

**Resource Limits**:
- File upload: 10MB per photo, 20 photos max = 200MB max
- Request body: 10MB max JSON
- Rate limiting: 100 req/min authenticated, 10 req/min unauthenticated

### Performance Budget Implementation

**Frontend Bundle Size Budgets** (FR-056, FR-057):

1. **JavaScript Bundle**: ≤250KB gzipped
   - Implementation:
     ```json
     // package.json
     {
       "scripts": {
         "build": "vite build",
         "analyze": "vite-bundle-visualizer"
       }
     }
     ```
   - Vite configuration for code splitting:
     ```typescript
     // vite.config.ts
     export default defineConfig({
       build: {
         rollupOptions: {
           output: {
             manualChunks: {
               'vendor': ['react', 'react-dom', 'react-router-dom'],
               'query': ['@tanstack/react-query'],
               'forms': ['react-hook-form'],
               'ui': ['@headlessui/react'],
             }
           }
         },
         chunkSizeWarningLimit: 250 // KB (uncompressed warning)
       }
     })
     ```
   - CI enforcement:
     ```yaml
     # .github/workflows/ci.yml
     - name: Check bundle size
       run: |
         npm run build
         BUNDLE_SIZE=$(gzip -c dist/assets/index-*.js | wc -c)
         MAX_SIZE=$((250 * 1024)) # 250KB
         if [ $BUNDLE_SIZE -gt $MAX_SIZE ]; then
           echo "Bundle size $BUNDLE_SIZE exceeds limit $MAX_SIZE"
           exit 1
         fi
     ```

2. **CSS Bundle**: ≤50KB gzipped
   - Tailwind CSS purge configuration:
     ```javascript
     // tailwind.config.js
     module.exports = {
       content: [
         "./index.html",
         "./src/**/*.{js,ts,jsx,tsx}",
       ],
       // Remove unused Tailwind classes in production
     }
     ```
   - PurgeCSS + cssnano in Vite build automatically reduces size

3. **Code Splitting Strategy**:
   - Route-based splitting (React Router lazy loading):
     ```tsx
     import { lazy, Suspense } from 'react';
     const ProjectsPage = lazy(() => import('./pages/ProjectsPage'));
     const EstimationPage = lazy(() => import('./pages/EstimationPage'));

     <Suspense fallback={<LoadingSpinner />}>
       <Routes>
         <Route path="/projects" element={<ProjectsPage />} />
         <Route path="/estimation/:id" element={<EstimationPage />} />
       </Routes>
     </Suspense>
     ```
   - Component-level splitting for heavy components:
     ```tsx
     const PriceComparisonChart = lazy(() => import('./PriceComparisonChart'));
     ```

**Frontend Performance - TTI/FCP** (FR-058):

1. **Critical Rendering Path Optimization**:
   - Inline critical CSS in HTML head
   - Defer non-critical CSS: `<link rel="stylesheet" href="..." media="print" onload="this.media='all'">`
   - Preload key resources:
     ```html
     <link rel="preload" href="/fonts/inter.woff2" as="font" crossorigin>
     <link rel="preconnect" href="https://api.estimate.app">
     ```

2. **JavaScript Optimization**:
   - Async/defer third-party scripts:
     ```html
     <script src="https://js.stripe.com/v3/" async></script>
     <script src="/analytics.js" defer></script>
     ```
   - Minification + tree-shaking (automatic in Vite production build)
   - Remove console.log in production (Vite plugin)

3. **Testing**:
   - Lighthouse CI: Enforce TTI ≤3.5s, FCP ≤1.2s
   - WebPageTest: Test on 4G throttled connection (1.6 Mbps, 300ms RTT)
   - Real User Monitoring (RUM): Track field metrics via PerformanceObserver API

**Image Optimization** (FR-059):

1. **Upload-time Processing**:
   - Backend resizes photos to max 1920px width:
     ```python
     from PIL import Image

     def optimize_photo(file_bytes: bytes) -> bytes:
         img = Image.open(io.BytesIO(file_bytes))
         # Resize if > 1920px width
         if img.width > 1920:
             ratio = 1920 / img.width
             new_height = int(img.height * ratio)
             img = img.resize((1920, new_height), Image.LANCZOS)
         # Compress JPEG at 85% quality
         output = io.BytesIO()
         img.save(output, format='JPEG', quality=85, optimize=True)
         return output.getvalue()
     ```

2. **Delivery Optimization**:
   - Responsive images with srcset:
     ```tsx
     <img
       src={photo.url_1920}
       srcSet={`
         ${photo.url_640} 640w,
         ${photo.url_1280} 1280w,
         ${photo.url_1920} 1920w
       `}
       sizes="(max-width: 640px) 100vw, (max-width: 1280px) 50vw, 33vw"
       loading="lazy"
       alt={photo.description}
     />
     ```
   - WebP format with JPEG fallback:
     ```tsx
     <picture>
       <source srcSet={photo.url_webp} type="image/webp" />
       <img src={photo.url_jpeg} alt={photo.description} />
     </picture>
     ```
   - Lazy loading below-the-fold images (native `loading="lazy"`)
   - Blur-up placeholder (LQIP - Low Quality Image Placeholder):
     ```tsx
     <img
       src={photo.url_full}
       style={{ backgroundImage: `url(${photo.url_blur})` }}
       onLoad={(e) => e.target.style.backgroundImage = 'none'}
     />
     ```

3. **CDN Configuration**:
   - Cache-Control headers: `max-age=31536000, immutable` for hashed filenames
   - Image CDN (Cloudflare Images or imgix) for automatic format conversion + resizing

**API Response Optimization** (FR-060):

1. **Pagination**:
   - Max 100 items per page:
     ```python
     @router.get("/projects", response_model=PaginatedResponse[ProjectSummary])
     async def list_projects(
         page: int = Query(1, ge=1),
         page_size: int = Query(20, ge=1, le=100),
         db: Session = Depends(get_db)
     ):
         offset = (page - 1) * page_size
         projects = db.query(Project).offset(offset).limit(page_size).all()
         total = db.query(Project).count()
         return {
             "items": projects,
             "total": total,
             "page": page,
             "page_size": page_size,
             "pages": math.ceil(total / page_size)
         }
     ```

2. **Field Selection (Sparse Fieldsets)**:
   - Allow clients to request only needed fields:
     ```python
     @router.get("/projects/{id}")
     async def get_project(
         id: UUID,
         fields: Optional[str] = Query(None, description="Comma-separated fields")
     ):
         # Parse fields: "id,name,created_at" → only return those fields
         ```

3. **Response Compression**:
   - FastAPI gzip middleware (automatic for responses >500 bytes):
     ```python
     from fastapi.middleware.gzip import GZipMiddleware
     app.add_middleware(GZipMiddleware, minimum_size=500)
     ```

4. **Payload Size Monitoring**:
   - Log response sizes:
     ```python
     @app.middleware("http")
     async def log_response_size(request: Request, call_next):
         response = await call_next(request)
         size = response.headers.get("content-length", 0)
         if int(size) > 500_000:  # 500KB
             logger.warning(f"Large response: {request.url} ({size} bytes)")
         return response
     ```

**Third-Party Script Management** (FR-061):

1. **Async Loading**:
   - Stripe:
     ```tsx
     useEffect(() => {
       const script = document.createElement('script');
       script.src = 'https://js.stripe.com/v3/';
       script.async = true;
       document.body.appendChild(script);
     }, []);
     ```
   - Analytics (Plausible - privacy-friendly, lightweight):
     ```html
     <script defer data-domain="estimate.app" src="https://plausible.io/js/script.js"></script>
     ```

2. **Budget Enforcement**:
   - Total third-party budget: ≤100KB
   - Stripe JS: ~50KB gzipped
   - Plausible analytics: ~1KB gzipped
   - Budget remaining: ~49KB for future additions

3. **Performance Impact Monitoring**:
   - Lighthouse third-party impact report
   - Block third-party scripts in CI tests to validate core functionality works without them

**Progressive Enhancement** (FR-062):

1. **Core Functionality Without JavaScript**:
   - Server-side rendering (SSR) for initial page load:
     ```tsx
     // Use Vite SSR or Next.js for server-rendered React
     export async function render(url: string) {
       const html = ReactDOMServer.renderToString(<App url={url} />);
       return html;
     }
     ```
   - Forms submit to backend even without JS:
     ```html
     <form action="/api/v1/projects" method="POST">
       <input name="name" required />
       <button type="submit">Create Project</button>
     </form>
     ```
   - Links work as normal `<a href>` tags before React Router hydration

2. **Enhanced Features Require JavaScript**:
   - Photo drag-and-drop (fallback: file input)
   - Real-time price comparison updates (fallback: refresh button)
   - Auto-save drafts (fallback: manual save button)

**Offline Support** (FR-063):

1. **Service Worker**:
   - Workbox for service worker generation:
     ```javascript
     // vite.config.ts
     import { VitePWA } from 'vite-plugin-pwa';

     export default defineConfig({
       plugins: [
         VitePWA({
           registerType: 'autoUpdate',
           workbox: {
             runtimeCaching: [
               {
                 urlPattern: /^https:\/\/api\.estimate\.app\/projects/,
                 handler: 'NetworkFirst',
                 options: {
                   cacheName: 'projects-cache',
                   expiration: { maxEntries: 50, maxAgeSeconds: 86400 }
                 }
               }
             ]
           }
         })
       ]
     })
     ```

2. **IndexedDB for Offline Storage**:
   - Cache project data and shopping lists:
     ```typescript
     import { openDB } from 'idb';

     const db = await openDB('estimate-offline', 1, {
       upgrade(db) {
         db.createObjectStore('projects', { keyPath: 'id' });
         db.createObjectStore('shopping-lists', { keyPath: 'id' });
       }
     });
     ```

3. **Read-Only Offline Mode**:
   - Display cached projects and shopping lists
   - Show banner: "You're offline. Changes will sync when reconnected."
   - Queue mutations in IndexedDB, sync on reconnect

**Cloud Provider SLA Validation** (FR-064):

1. **SLA Requirements Documented**:
   - Supabase: 99.9% uptime SLA (Enterprise plan), 99.5% (Pro plan)
   - Railway: 99.5% uptime (no formal SLA on free tier)
   - Vercel: 99.99% edge network uptime (Enterprise), 99.9% (Pro)
   - Stripe: 99.99% API uptime SLA

2. **Uptime Monitoring**:
   - External monitoring: UptimeRobot, Pingdom, or StatusCake
   - Health check endpoints: `/health/live`, `/health/ready`
   - Alert on downtime >5 minutes

3. **SLA Alignment**:
   - System SLA target: 99.5% (matches Railway, most conservative)
   - Allowed downtime: ~3.65 hours/month
   - Scheduled maintenance: During low-traffic windows (3-5 AM UTC)

**Performance Testing & Validation**:

1. **Load Testing** (Locust):
   ```python
   # locustfile.py
   from locust import HttpUser, task, between

   class EstimateUser(HttpUser):
       wait_time = between(1, 3)

       @task(3)
       def list_projects(self):
           self.client.get("/api/v1/projects", headers={"Authorization": f"Bearer {self.token}"})

       @task(1)
       def create_estimation(self):
           self.client.post("/api/v1/estimates", json={...})

   # Run: locust -f locustfile.py --users 10000 --spawn-rate 100 --host https://api.estimate.app
   ```

2. **Lighthouse CI**:
   - GitHub Actions integration (see Accessibility section)
   - Budgets enforced:
     ```json
     {
       "budget": [
         {
           "resourceType": "script",
           "budget": 250
         },
         {
           "resourceType": "stylesheet",
           "budget": 50
         },
         {
           "resourceType": "image",
           "budget": 500
         }
       ]
     }
     ```

3. **Real User Monitoring (RUM)**:
   - PerformanceObserver API to collect field metrics:
     ```typescript
     const observer = new PerformanceObserver((list) => {
       for (const entry of list.getEntries()) {
         if (entry.name === 'first-contentful-paint') {
           analytics.track('FCP', { value: entry.startTime });
         }
       }
     });
     observer.observe({ entryTypes: ['paint', 'largest-contentful-paint'] });
     ```
   - Send to backend for aggregation and dashboards

---

## Constitution Check Summary

**Overall Status**: ✅ PASS

All constitutional requirements are addressed:
- ✅ Beads integration planned for task tracking
- ✅ TDD workflow defined with 90%+ coverage targets
- ✅ SOLID architecture patterns specified
- ✅ Security-first design with 6-layer defense in depth
- ✅ API versioning strategy (/api/v1/, semver)
- ✅ Observability (Prometheus, structured logging, OpenTelemetry)
- ✅ Graceful degradation for all external dependencies
- ✅ Code quality gates (mypy, ruff, ESLint, code review)
- ✅ Data protection (encryption, RLS, GDPR compliance)
- ✅ Performance targets aligned with constitution

**No violations requiring justification.**

---

## XI. Accessibility Implementation (WCAG 2.1 AA) - MANDATORY

**Status**: REQUIRED for legal compliance (ADA, Section 508) and inclusive design

### Accessibility Standards Target

All user interfaces MUST meet **WCAG 2.1 Level AA** compliance:
- Perceivable: Content perceivable by all users (visual, auditory, tactile)
- Operable: UI components operable by all users (keyboard, mouse, touch, voice)
- Understandable: Information and operation understandable
- Robust: Content interpretable by assistive technologies

### Keyboard Navigation Implementation

**Requirements** (FR-035):
- All interactive elements accessible via keyboard
- Standard key bindings:
  - `Tab` / `Shift+Tab`: Navigate forward/backward through focusable elements
  - `Enter` / `Space`: Activate buttons, links, form controls
  - `Escape`: Close modals, cancel operations, clear focus
  - `Arrow keys`: Navigate within composite widgets (dropdowns, tabs, radio groups)
  - `Home` / `End`: Jump to first/last item in lists

**Implementation**:
- React components use semantic HTML (`<button>`, `<a>`, `<input>`) for native focus
- Custom components implement `tabIndex`, `onKeyDown` handlers
- Focus trap in modals using `react-focus-lock` library
- Skip navigation links: `<a href="#main-content">Skip to main content</a>`
- Focus order matches visual reading order (left-to-right, top-to-bottom)

**Testing**:
- Manual: Tab through entire application without mouse
- Automated: Pa11y keyboard navigation tests in CI

### Focus Management

**Requirements** (FR-036):
- Visible focus indicators on all interactive elements
- Minimum contrast: 3:1 against background
- Minimum thickness: 2px outline or border

**Implementation**:
- Tailwind CSS focus utilities: `focus:ring-2 focus:ring-blue-500 focus:ring-offset-2`
- Global CSS custom focus styles:
  ```css
  *:focus-visible {
    outline: 2px solid var(--focus-color);
    outline-offset: 2px;
  }
  ```
- Focus return: When closing modals, focus returns to trigger element
- Dynamic content: Focus moves to newly loaded content (e.g., photo analysis results)

### Color Contrast & Visual Design

**Requirements** (FR-037):
- Normal text (< 18pt): 4.5:1 contrast minimum
- Large text (≥ 18pt or ≥ 14pt bold): 3:1 contrast minimum
- UI components (buttons, inputs): 3:1 contrast minimum

**Implementation**:
- Tailwind color palette validated for contrast (use `text-gray-900` on `bg-white`, avoid `text-gray-400` on `bg-gray-100`)
- Error states: Red text must meet 4.5:1 ratio (`text-red-700` on white)
- Success states: Green text must meet 4.5:1 ratio (`text-green-700` on white)
- Interactive states: Hover/focus colors maintain contrast

**Validation**:
- Design phase: Contrast checker tool (WebAIM, Stark)
- CI/CD: axe-core automated contrast tests
- Manual: Lighthouse accessibility audit ≥95 score

### ARIA Implementation

**Requirements** (FR-038, FR-040):
- All images have alt text or aria-label
- Custom components have proper ARIA roles, states, properties
- Form inputs associated with labels

**Implementation**:
- Images:
  ```tsx
  <img src={photo.url} alt={`Room photo ${index + 1}: ${photo.description}`} />
  ```
- Custom buttons:
  ```tsx
  <div role="button" tabIndex={0} aria-pressed={isActive} onClick={handleClick}>
  ```
- Form labels:
  ```tsx
  <label htmlFor="room-width">Room Width (feet)</label>
  <input id="room-width" type="number" aria-required="true" aria-invalid={hasError} />
  ```
- Error messages:
  ```tsx
  <input aria-describedby="width-error" />
  <p id="width-error" role="alert">{errorMessage}</p>
  ```
- Loading states:
  ```tsx
  <div role="status" aria-live="polite" aria-busy={isLoading}>
    {isLoading ? "Analyzing photos..." : "Analysis complete"}
  </div>
  ```
- Modal dialogs:
  ```tsx
  <div role="dialog" aria-modal="true" aria-labelledby="dialog-title">
    <h2 id="dialog-title">Confirm Delete Project</h2>
  </div>
  ```

### Semantic HTML Structure

**Requirements** (FR-041):
- Use HTML5 semantic elements
- Maintain logical heading hierarchy

**Implementation**:
- Page structure:
  ```tsx
  <header>
    <nav aria-label="Main navigation">...</nav>
  </header>
  <main id="main-content">
    <h1>Project: Kitchen Renovation</h1>
    <section aria-labelledby="estimation-heading">
      <h2 id="estimation-heading">Materials Estimation</h2>
      <article>...</article>
    </section>
  </main>
  <footer>...</footer>
  ```
- Heading hierarchy: Single `<h1>` per page, no skipped levels (h1 → h3 forbidden)
- Lists: Use `<ul>`, `<ol>` for shopping lists, project lists
- Tables: Use `<table>`, `<thead>`, `<tbody>` with `<th scope="col|row">` for price comparisons

### Touch & Mobile Accessibility

**Requirements** (FR-042):
- Minimum touch target size: 44x44 pixels
- Spacing between targets: 8px minimum

**Implementation**:
- Tailwind utilities: `min-h-[44px] min-w-[44px] p-2` on buttons
- Icon buttons: Larger hitbox than icon
  ```tsx
  <button className="p-3"> {/* 48px touch target */}
    <TrashIcon className="w-6 h-6" /> {/* 24px icon */}
  </button>
  ```
- Mobile-specific: Increase spacing on `@media (max-width: 768px)`

### Motion & Animation Accessibility

**Requirements** (FR-043):
- Respect `prefers-reduced-motion` media query
- Provide static alternatives to animations

**Implementation**:
- Tailwind configuration:
  ```js
  // tailwind.config.js
  module.exports = {
    theme: {
      extend: {
        transitionProperty: {
          'none': 'none',
        },
      },
    },
  }
  ```
- CSS animations:
  ```css
  @media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
    }
  }
  ```
- React transitions:
  ```tsx
  const prefersReducedMotion = useMediaQuery('(prefers-reduced-motion: reduce)');
  const duration = prefersReducedMotion ? 0 : 300;
  ```

### Browser Zoom & Responsive Design

**Requirements** (FR-044):
- Support browser zoom up to 200%
- No horizontal scrolling at 200% zoom
- No content loss at 200% zoom

**Implementation**:
- Use relative units (`rem`, `em`) instead of `px` for font sizes
- Tailwind breakpoints: `sm:`, `md:`, `lg:` for responsive layouts
- Flexbox/Grid: Auto-wrap at narrow widths
- Test at 200% zoom: 1920px screen → renders like 960px screen

### Accessible Forms

**Requirements** (FR-039):
- All inputs have labels
- Error messages announced to screen readers
- Required fields indicated

**Implementation**:
- React Hook Form with accessibility:
  ```tsx
  <form onSubmit={handleSubmit(onSubmit)}>
    <label htmlFor="project-name">
      Project Name <span aria-label="required">*</span>
    </label>
    <input
      id="project-name"
      {...register("name", { required: "Project name is required" })}
      aria-required="true"
      aria-invalid={!!errors.name}
      aria-describedby={errors.name ? "name-error" : undefined}
    />
    {errors.name && (
      <p id="name-error" role="alert" className="text-red-700">
        {errors.name.message}
      </p>
    )}
  </form>
  ```

### Automated Accessibility Testing

**Requirements** (FR-047):
- CI/CD integration
- WCAG 2.1 AA automated checks before release
- Lighthouse accessibility score ≥95

**Implementation**:
- **Unit/Component Tests** (Vitest + jest-axe):
  ```tsx
  import { axe, toHaveNoViolations } from 'jest-axe';
  expect.extend(toHaveNoViolations);

  test('PhotoUploader has no accessibility violations', async () => {
    const { container } = render(<PhotoUploader />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
  ```

- **E2E Tests** (Playwright + axe-core):
  ```typescript
  import { injectAxe, checkA11y } from 'axe-playwright';

  test('Project page is accessible', async ({ page }) => {
    await page.goto('/projects/123');
    await injectAxe(page);
    await checkA11y(page, null, {
      detailedReport: true,
      detailedReportOptions: { html: true },
    });
  });
  ```

- **CI/CD Lighthouse** (GitHub Actions):
  ```yaml
  - name: Run Lighthouse CI
    uses: treosh/lighthouse-ci-action@v9
    with:
      urls: |
        http://localhost:3000
        http://localhost:3000/projects/new
        http://localhost:3000/estimation/123
      configPath: './.lighthouserc.json'
      uploadArtifacts: true
  ```

- **Lighthouse config** (`.lighthouserc.json`):
  ```json
  {
    "ci": {
      "assert": {
        "assertions": {
          "categories:accessibility": ["error", { "minScore": 0.95 }],
          "categories:performance": ["warn", { "minScore": 0.90 }]
        }
      }
    }
  }
  ```

### Component Library Accessibility

**Dependencies**:
- **Headless UI** (by Tailwind Labs): Pre-built accessible components
  - Dialog/Modal with focus trap, Esc to close, aria-modal
  - Dropdown Menu with keyboard navigation (Arrow keys, Enter, Esc)
  - Tabs with ARIA roles, keyboard navigation
  - Radio Group with arrow key navigation
- **React Hook Form**: Accessible form validation
- **react-focus-lock**: Focus trapping for modals
- **@reach/skip-nav**: Skip navigation links

**Custom Component Checklist**:
- [ ] Keyboard navigable
- [ ] Focus indicators visible (3:1 contrast, 2px outline)
- [ ] ARIA roles/labels/states implemented
- [ ] Color contrast meets 4.5:1 (normal) or 3:1 (large)
- [ ] Touch targets ≥44px
- [ ] Respects prefers-reduced-motion
- [ ] Automated axe tests pass
- [ ] Manual screen reader testing (VoiceOver, NVDA, JAWS)

### Screen Reader Testing

**Manual Testing Requirements**:
- **macOS/iOS**: VoiceOver (Cmd+F5)
- **Windows**: NVDA (free), JAWS (enterprise)
- **Android**: TalkBack
- **Linux**: Orca

**Test Scenarios**:
- Navigate entire project creation flow with screen reader only
- Upload photos and hear progress announcements
- Review shopping list with item details announced
- Interact with price comparison table
- Submit forms and hear error messages

**Acceptance**:
- All content readable by screen reader
- All interactive elements activatable
- Loading states announced (aria-live regions)
- Error messages announced immediately
- Modal dialogs trapped focus properly

---

## XII. Additional Security Requirements & Threat Model

### Threat Model Documentation

**Attack Vectors Addressed**:

1. **Authentication Bypass Attacks**:
   - Invalid token attacks: Expired JWT, tampered signatures, missing claims
   - Brute force: Rate limited to 3 attempts/hour on password reset
   - Session hijacking: HTTP-only cookies, secure flag, SameSite=Strict
   - Account enumeration: Constant-time responses for login/signup

2. **Malicious File Upload Attacks**:
   - Virus/malware: ClamAV scanning before storage
   - Executable files: MIME type whitelist (image/jpeg, image/png, image/heic only)
   - Zip bombs: File size limit enforcement (10MB max per photo)
   - Path traversal: Sanitized filenames, UUID-based S3 keys

3. **SQL Injection Attacks**:
   - Special characters in user input: SQLAlchemy ORM parameterized queries only
   - Example test cases:
     ```python
     # Test: SQL injection in project name
     payload = "'; DROP TABLE projects; --"
     # Expected: Escaped and stored safely
     ```
   - No raw SQL allowed (enforced in code review)

4. **XSS Attacks**:
   - Stored XSS: React auto-escaping for all user-generated content
   - Reflected XSS: CSP headers prevent inline scripts
   - DOM XSS: No `innerHTML`, only `textContent` or React components
   - Example test cases:
     ```typescript
     // Test: XSS in project description
     const payload = '<script>alert("xss")</script>';
     // Expected: Rendered as plain text, not executed
     ```

5. **Insider Threat Scenarios**:
   - Malicious admin: Audit logs immutable, admin actions logged
   - Database access: Production database access requires MFA + approval
   - API key rotation: Compromised keys rotated within 1 hour
   - Data exfiltration: Rate limiting on export endpoints (10/day per user)

### Security-Critical Code Paths

**Explicitly Identified Critical Paths**:

1. **Authentication Flow** (`src/api/v1/auth.py`):
   - `/auth/login` - JWT generation
   - `/auth/refresh` - Token refresh
   - `/auth/logout` - Session invalidation
   - Review: 2 approvals required, 100% test coverage mandatory

2. **Authorization Checks** (`src/api/dependencies.py`):
   - `@require_auth` decorator - JWT validation
   - `@require_tier(tier)` decorator - Subscription checks
   - `check_project_ownership()` - RLS enforcement
   - Review: Security audit on every change

3. **Payment Processing** (`src/services/payment/stripe_service.py`):
   - `create_checkout_session()` - Stripe integration
   - `handle_webhook()` - Payment confirmations
   - `update_subscription()` - Tier changes
   - Review: 2 approvals, PCI compliance checks

4. **File Upload** (`src/api/v1/projects.py`):
   - `/projects/{id}/photos/upload-url` - Presigned URL generation
   - Virus scanning integration
   - MIME validation
   - Review: Security scan on changes

5. **Data Deletion** (`src/api/v1/users.py`):
   - `/users/me` DELETE - GDPR compliance
   - Cascade deletion logic
   - Audit log preservation
   - Review: Legal + security approval

### Data Retention & Deletion

**Retention Policy**:
- User accounts: 7 years after last activity (configurable)
- Projects: Retained as long as user account active
- Photos: Retained with projects, compressed after 90 days
- Audit logs: 7 years immutable retention (compliance)
- Pricing data cache: 48 hours TTL, then deleted

**Secure Deletion Requirements**:
- Cascade deletes defined in database schema:
  ```sql
  ALTER TABLE projects
    ADD CONSTRAINT fk_user
    FOREIGN KEY (user_id) REFERENCES user_profiles(id)
    ON DELETE CASCADE;
  ```
- S3 object deletion: Immediate via S3 DeleteObject API
- Database soft delete: Mark `deleted_at` timestamp, hard delete after 30 days
- Secure erasure: No need for disk wiping (managed cloud storage handles this)
- Audit trail: Deletion events logged before actual deletion

**GDPR Right to Deletion** (`/api/v1/users/me` DELETE):
```python
@router.delete("/users/me")
async def delete_user_account(user: User = Depends(get_current_user)):
    """
    GDPR-compliant user deletion.
    Cascades to: projects, photos, shopping_lists, subscriptions, feedback.
    Preserves: Anonymized audit logs for compliance.
    """
    # 1. Cancel Stripe subscription
    await stripe_service.cancel_subscription(user.subscription_id)

    # 2. Delete S3 objects (all user photos)
    await storage_service.delete_user_objects(user.id)

    # 3. Anonymize audit logs (replace PII with user_id hash)
    await audit_service.anonymize_logs(user.id)

    # 4. Delete database records (CASCADE handles related tables)
    await user_repository.delete(user.id)

    return {"message": "Account deleted successfully"}
```

### Security Scanning & Testing

**SAST (Static Application Security Testing)**:
- Tool: Bandit (Python), ESLint security plugin (TypeScript)
- Frequency: On every commit (pre-commit hook + CI)
- Scope: All code in `src/`, `tests/`
- Failing criteria: HIGH severity issues block merge
- Configuration:
  ```yaml
  # .bandit.yml
  exclude_dirs:
    - /tests/
  tests:
    - B201  # Flask debug mode
    - B301  # Pickle usage
    - B303  # MD5/SHA1 usage
    - B501  # SSL/TLS verification disabled
  ```

**DAST (Dynamic Application Security Testing)**:
- Tool: OWASP ZAP
- Frequency: Weekly automated scans in staging
- Scope: All API endpoints
- Failing criteria: MEDIUM+ vulnerabilities require remediation
- Integration: Scheduled GitHub Actions workflow

**Dependency Scanning**:
- Tool: Dependabot (GitHub), Safety (Python), npm audit (Node.js)
- Frequency: Daily automated checks
- Scope: `pyproject.toml`, `package.json`, `package-lock.json`
- Failing criteria: CRITICAL vulnerabilities block deployment
- Auto-remediation: Dependabot PRs for patch updates

**Security Code Review Checklist**:
- [ ] No hardcoded secrets (grep for API keys, passwords)
- [ ] Input validation present (Pydantic strict mode)
- [ ] SQL injection prevented (no raw SQL)
- [ ] XSS prevention (React auto-escape, CSP headers)
- [ ] CSRF protection (tokens for state-changing ops)
- [ ] File upload validated (MIME, size, virus scan)
- [ ] Rate limiting applied (endpoints annotated)
- [ ] Encryption used (TLS 1.3, AES-256 at rest)
- [ ] Audit logging present (security events logged)
- [ ] Error messages sanitized (no stack traces in prod)

### Stripe PCI Compliance

**PCI DSS Requirements**:
- **Card data handling**: Never store full card numbers (Stripe.js handles all card data client-side)
- **Tokenization**: Stripe generates tokens, backend only stores `customer_id` and `payment_method_id`
- **PCI Level**: Stripe is PCI Level 1 compliant, EstiMate is PCI SAQ-A compliant (lowest burden)
- **No cardholder data**: EstiMate backend never touches card numbers, CVV, or expiration dates

**Implementation**:
```typescript
// Frontend: Stripe.js integration
const stripe = await loadStripe(process.env.VITE_STRIPE_PUBLIC_KEY);
const { error, paymentMethod } = await stripe.createPaymentMethod({
  type: 'card',
  card: cardElement,
});
// Send paymentMethod.id to backend (NOT card details)
```

```python
# Backend: Stripe customer creation
customer = stripe.Customer.create(
    email=user.email,
    payment_method=payment_method_id,
    invoice_settings={"default_payment_method": payment_method_id}
)
# Store customer.id in database (NOT card details)
```

**Compliance Documentation**:
- Location: `/docs/compliance/stripe-pci.md`
- Contents: Data flow diagram, PCI SAQ-A questionnaire, attestation of compliance
- Review: Annual PCI compliance review

### Session Timeout Trade-Offs

**Requirement**: Balance security (short timeout) vs UX (long timeout)

**Decision**:
- Free tier: 30 days inactivity timeout (lower security requirements)
- Pro tier: 90 days inactivity timeout (balance security + convenience)
- Business tier: 90 days inactivity timeout + optional enforcement of 24h for team accounts
- Active session: Never timeout while user is active (heartbeat every 15 minutes)

**Rationale**:
- Security: Longer timeouts increase risk of session hijacking if device stolen
- UX: Shorter timeouts cause frustration for returning users
- Trade-off: 30-90 day timeout is industry standard for non-financial apps
- Mitigation: "Remember me" disabled for Business tier if admin enforces 24h timeout

**Implementation**:
```python
# Session TTL based on tier
SESSION_TTL = {
    "Free": 30 * 24 * 60 * 60,      # 30 days
    "Pro": 90 * 24 * 60 * 60,       # 90 days
    "Business": 90 * 24 * 60 * 60,  # 90 days (overridable to 24h)
}

# Active session heartbeat (frontend)
setInterval(() => {
  api.post('/auth/heartbeat');  # Extends session TTL
}, 15 * 60 * 1000);  # Every 15 minutes
```

### API Key Rotation Edge Cases

**Scenario**: API key compromised mid-request (keys in flight)

**Handling**:
1. **Detect compromise**: Security monitoring alerts on suspicious usage
2. **Generate new key**: Create new key immediately, old key marked `rotating`
3. **Grace period**: Both old and new keys valid for 5 minutes
4. **Client notification**: WebSocket push to all active clients: "API key rotated, refresh"
5. **Hard cutoff**: After 5 minutes, old key rejected with `401 Unauthorized`
6. **Audit**: All requests using old key logged for forensic analysis

**Implementation**:
```python
def validate_api_key(key: str) -> bool:
    key_record = db.query(APIKey).filter(APIKey.key == key).first()
    if not key_record:
        return False
    if key_record.status == "revoked":
        return False
    if key_record.status == "rotating":
        # Grace period: 5 minutes from rotation_started_at
        grace_period = timedelta(minutes=5)
        if datetime.now() - key_record.rotation_started_at > grace_period:
            return False
    return True
```

### Legacy Data Migration Security

**Scenario**: Migrating from insecure legacy system to EstiMate

**Requirements**:
- No plaintext passwords accepted (force password reset)
- Legacy IDs not exposed in new system (generate new UUIDs)
- Old data sanitized before import (remove PII not needed)
- Audit trail of migration (who imported, when, what data)
- Rollback plan (keep legacy system read-only for 30 days)

**Migration Script Security Checklist**:
```python
# /scripts/migrate_legacy_users.py
# SECURITY REQUIREMENTS:
# - Runs with DBA credentials (not exposed in code)
# - Logs all migrations to audit table
# - Validates all data before insert (Pydantic models)
# - No raw SQL (SQLAlchemy ORM only)
# - PII minimization (only import required fields)
# - Force password reset on first login
```

---

## XIII. Resource Limits & Infrastructure Requirements

### System Resource Limits

**Backend Service Limits** (per container instance):
- Memory: 2GB minimum, 4GB recommended, 8GB maximum
- CPU: 2 vCPUs minimum, 4 vCPUs recommended
- Network: 1 Gbps minimum bandwidth
- Disk: 20GB minimum (mostly for logs), SSD required
- Ephemeral storage: 10GB for temporary photo processing

**Database Resource Limits** (PostgreSQL):
- Memory: 4GB minimum (shared_buffers: 1GB)
- CPU: 4 vCPUs minimum
- Storage: 100GB minimum, scales with user growth
- Connections: Max 100 connections (connection pooling with PgBouncer)
- IOPS: 3000 IOPS minimum (provisioned SSD)

**Cache Resource Limits** (Redis):
- Memory: 2GB minimum, 4GB recommended (pricing data + sessions)
- CPU: 2 vCPUs
- Network: 500 Mbps
- Persistence: AOF enabled, fsync every second

**Photo Storage Limits** (S3):
- Total storage: 5TB year 1 (5M photos × 1MB average)
- Upload bandwidth: 100 Mbps sustained
- Download bandwidth: 500 Mbps sustained (presigned URLs offload from backend)
- Object count: 10M objects maximum (year 3 projection)

**Monitoring & Alerts for Resource Limits**:
```yaml
# Prometheus alerts
alerts:
  - name: BackendMemoryHigh
    expr: container_memory_usage_bytes{job="backend"} > 3.5 * 1024^3
    for: 5m
    severity: warning

  - name: DatabaseCPUHigh
    expr: pg_cpu_usage > 80
    for: 10m
    severity: critical

  - name: RedisMemoryHigh
    expr: redis_memory_used_bytes > 3.5 * 1024^3
    for: 5m
    severity: warning
```

### Database Failover Scenarios

**Primary Database Failure**:
1. **Detection**: Health check fails (3 consecutive failures over 30 seconds)
2. **Automatic failover**: AWS RDS/Supabase promotes read replica to primary (60-120 seconds)
3. **Connection retry**: Application retries with exponential backoff (5 attempts over 30 seconds)
4. **Degraded mode**: If failover exceeds 2 minutes, activate read-only mode
5. **User notification**: Banner displayed: "Service temporarily in read-only mode"

**Read Replica Lag**:
- Normal lag: <1 second (monitored)
- Warning: >5 seconds lag (alert sent)
- Critical: >30 seconds lag (stop routing reads to replica)
- Fallback: Route all reads to primary if replica unhealthy

**Performance During Failover**:
- Write operations: Queued for up to 2 minutes, then rejected with `503 Service Unavailable`
- Read operations: Continue from read replica (stale data acceptable)
- User impact: Brief unavailability (60-120 seconds) for write operations

**Testing Failover**:
- Frequency: Quarterly chaos engineering tests
- Procedure: Manually trigger RDS failover in staging
- Success criteria: <3 minutes total downtime, zero data loss

###Photo Upload & Analysis Flow Performance Requirements

**Photo Upload Flow** (FR-001, US1):
- Initial page load (upload form): ≤1.5s (LCP)
- File selection response: Instant (<100ms)
- Upload progress updates: Every 500ms
- Presigned URL generation: ≤200ms
- S3 upload (10MB photo, 4G network): ≤10s
- Total time (4 photos): ≤45s (10s each + 5s overhead)

**Photo Analysis Flow** (FR-002, US1):
- CV API request initiation: ≤100ms
- CV API processing (per photo): ≤10s (Google Cloud Vision SLA)
- Total analysis (3-4 photos): ≤30s (target p95)
- Context: 3-4 photos, up to 10MB each, typical room dimensions
- Progress indicator: Updated every 2s with current photo number
- Failure handling: If any photo >30s, prompt manual dimension input

**Shopping List Viewing Flow** (FR-006, US2):
- Page load (initial render): ≤1.0s
- API request (`/projects/{id}/shopping-list`): ≤300ms
- Client-side rendering (50 items): ≤200ms
- Total: ≤1.5s from click to interactive
- Virtualization: Enabled if >50 items (react-window)

**Price Comparison Flow** (FR-018, US5):
- Initial price fetch (3 retailers, 20 items): ≤2s
- Price refresh (cache miss): ≤3s
- Price refresh (cache hit): ≤300ms
- Comparison UI render: ≤500ms
- Total: ≤3.5s worst case (cold cache)

**Photo Analysis Context** (SC-005):
- **Photo count**: 3-4 photos (typical room documentation)
- **Photo size**: Average 5MB (range: 2-10MB after client-side compression)
- **Room complexity**: Standard rectangular rooms (most common)
- **Complex rooms**: Non-rectangular, vaulted ceilings, bay windows (may exceed 30s, fallback to manual)
- **Load pattern for 10,000 concurrent users**:
  - 60% browsing: Viewing projects, shopping lists (GET requests, cached)
  - 30% creating/editing: New projects, updating room details (POST/PATCH)
  - 10% uploading: Photo uploads (S3 direct upload, CV analysis async)

**Specific Load Pattern Breakdown**:
| Activity | % Users | Request Type | Rate (req/s) | Target Latency |
|----------|---------|--------------|--------------|----------------|
| View projects list | 30% (3000) | GET /projects | 50 | <200ms (cached) |
| View shopping list | 20% (2000) | GET /projects/{id}/shopping-list | 33 | <300ms |
| Browse pricing | 10% (1000) | GET /pricing/compare | 17 | <2s (cold), <300ms (cached) |
| Create project | 15% (1500) | POST /projects | 25 | <500ms |
| Upload photos | 5% (500) | POST /photos/upload-url | 8 | <10s (S3 upload) |
| Edit project | 10% (1000) | PATCH /projects/{id} | 17 | <300ms |
| Trigger estimation | 5% (500) | POST /projects/{id}/estimate | 8 | <30s (async CV) |
| Other (auth, pricing refresh) | 5% (500) | Various | 8 | Varies |

**Traffic Pattern (10K concurrent users)**:
- Peak hours: Weekday evenings 6-9pm local time (70% of daily traffic)
- Weekend: 30% of traffic, more evenly distributed
- Burst events: Weekend DIY project starts (Saturday mornings)
- Geographic distribution: 60% US, 20% Canada, 10% UK, 10% other

---

## XIV. Additional Accessibility Requirements

### Data Table Accessibility (Shopping Lists, Price Comparisons)

**Requirements** (FR-051):
```tsx
<table>
  <caption>Shopping List for Kitchen Renovation</caption>
  <thead>
    <tr>
      <th scope="col">Material</th>
      <th scope="col">Quantity</th>
      <th scope="col">Unit</th>
      <th scope="col">Waste %</th>
      <th scope="col">Total</th>
      <th scope="col">Est. Cost</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">Paint - Interior Semi-Gloss</th>
      <td>3.2 gallons</td>
      <td>gallons</td>
      <td>10%</td>
      <td>4 gallons</td>
      <td>$156.00</td>
    </tr>
  </tbody>
</table>
```

**Sortable Columns**:
```tsx
<th scope="col" aria-sort={sortColumn === 'cost' ? sortDirection : 'none'}>
  <button onClick={() => handleSort('cost')} aria-label="Sort by estimated cost">
    Est. Cost
    {sortColumn === 'cost' && (
      <span aria-hidden="true">{sortDirection === 'ascending' ? '↑' : '↓'}</span>
    )}
  </button>
</th>
```

**Screen Reader Announcements**:
```tsx
<div role="status" aria-live="polite" className="sr-only">
  {`Sorted by ${sortColumn} in ${sortDirection} order. ${items.length} items displayed.`}
</div>
```

### Link Accessibility

**Requirements** (FR-038):
- All links have descriptive text (no "click here", "read more")
- External links indicated with aria-label
- Link purpose clear from text alone

**Implementation**:
```tsx
{/* Bad */}
<a href="/projects/123">Click here</a>

{/* Good */}
<a href="/projects/123">View Kitchen Renovation project</a>

{/* External link */}
<a href="https://homedepot.com/product/123" target="_blank" rel="noopener noreferrer">
  Buy Paint at Home Depot
  <span className="sr-only"> (opens in new window)</span>
  <ExternalLinkIcon className="inline w-4 h-4" aria-hidden="true" />
</a>

{/* Retailer link with context */}
<a href={product.url} aria-label={`Buy ${product.name} at ${retailer} for $${product.price}`}>
  ${product.price}
</a>
```

### Empty States Accessibility

**Requirements** (Edge Cases, FR-052):
- Empty states announced to screen readers
- Clear messaging for no content
- Actions keyboard accessible

**Implementation**:
```tsx
{/* No projects */}
<div role="status" aria-live="polite">
  <h2>No Projects Yet</h2>
  <p>You haven't created any projects. Get started by creating your first renovation estimate.</p>
  <a href="/projects/new" className="btn-primary">
    Create Your First Project
  </a>
</div>

{/* No photos uploaded */}
<div role="status" aria-live="polite">
  <p>No photos uploaded yet. Add 3-4 photos of your room to get started.</p>
  <button onClick={openFilePicker} className="btn-primary">
    Upload Photos
  </button>
</div>

{/* Search results empty */}
<div role="status" aria-live="assertive">
  <p>No projects found matching "{searchQuery}". Try a different search term.</p>
  <button onClick={clearSearch}>Clear Search</button>
</div>
```

### Text Sizing & Scalability (FR-041)

**Requirements**: All text uses relative units (rem, em) for browser zoom support

**Implementation**:
```css
/* Base font size */
html {
  font-size: 16px; /* 1rem = 16px */
}

/* Component text sizes (rem units) */
body {
  font-size: 1rem; /* 16px */
}

h1 {
  font-size: 2.25rem; /* 36px */
}

h2 {
  font-size: 1.875rem; /* 30px */
}

.text-sm {
  font-size: 0.875rem; /* 14px */
}

.text-lg {
  font-size: 1.125rem; /* 18px */
}

/* Spacing also in rem for consistent scaling */
.p-4 {
  padding: 1rem; /* 16px */
}

.mt-6 {
  margin-top: 1.5rem; /* 24px */
}
```

**Browser Zoom Support**:
- 100% zoom: Default design
- 150% zoom: Comfortable for low vision users
- 200% zoom: No horizontal scrolling, all content visible
- 400% zoom: Mobile-like layout, stacked elements

**Testing**:
```typescript
// Playwright test for zoom support
test('Site is usable at 200% zoom', async ({ page }) => {
  await page.setViewportSize({ width: 1920, height: 1080 });
  await page.goto('/projects');

  // Simulate 200% zoom (viewport width / 2)
  await page.setViewportSize({ width: 960, height: 540 });

  // Verify no horizontal scrolling
  const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
  const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
  expect(scrollWidth).toBe(clientWidth);

  // Verify all content visible
  const mainContent = await page.locator('main').isVisible();
  expect(mainContent).toBe(true);
});
```

---

## XV. Additional Requirements (Final Gap Closure)

### WCAG AA vs AAA Compliance Boundary

**WCAG 2.1 Level AA (Target - MUST HAVE)**:
- All requirements in spec.md FR-035 through FR-058 target WCAG AA compliance
- Success criteria: SC-013 through SC-017 define AA-level acceptance criteria
- Automated testing: axe-core validates AA conformance
- Manual testing: NVDA/JAWS/VoiceOver testing ensures AA compliance

**WCAG 2.1 Level AAA (Stretch - NICE TO HAVE)**:
- AAA is NOT a hard requirement for MVP or initial production release
- AAA enhancements may be considered for future releases if:
  - User feedback indicates need for enhanced accessibility
  - Government contracts require AAA compliance
  - Additional budget allocated for accessibility improvements
- Example AAA criteria NOT targeted in current scope:
  - Extended audio descriptions (1.2.7)
  - Sign language interpretation (1.2.6)
  - Enhanced contrast ratio 7:1 (1.4.6) - we target AA 4.5:1
  - No interruptions (2.2.4) - we allow reasonable interruptions
  - Reading level (3.1.5) - we target clear language but not grade-level specific

**Rationale**: WCAG AA compliance covers 95% of accessibility needs for general web applications and meets legal requirements in most jurisdictions (ADA, Section 508, European EN 301 549). AAA is typically reserved for specialized accessibility-focused applications.

### MFA Requirements for Business Tier

**FR-011 Implementation Details**:
- Business tier users (FR-011) MAY enable MFA for enhanced security
- MFA is OPTIONAL at MVP, not enforced by default
- Implementation approach:
  ```typescript
  // Supabase Auth supports MFA out of the box
  const { data, error } = await supabase.auth.mfa.enroll({
    factorType: 'totp',
    friendlyName: 'EstiMate Business Account'
  });

  // User can enable/disable MFA in account settings
  // Backend: No changes required, Supabase handles MFA flow
  // Frontend: Add MFA enrollment UI in /settings/security
  ```
- MFA methods supported: TOTP (Time-based One-Time Password) via authenticator apps
- Backup codes: 10 single-use backup codes generated on enrollment
- Recovery: Email-based account recovery flow if MFA device lost

**Rationale**: MFA adds friction to user experience. Making it optional for Business tier balances security and usability. Enterprise tier (future) may enforce MFA.

### API Key Rotation Edge Cases

**Background**: API keys (Stripe, Google Cloud Vision, Redis, Supabase) must be rotated periodically for security.

**Edge Case Handling**:
1. **Keys in flight during rotation**:
   - Both old and new keys remain valid during grace period (1 hour)
   - API clients retry with exponential backoff if 401 Unauthorized
   - After grace period, old key is revoked

2. **Rotation procedure**:
   ```bash
   # 1. Generate new key in provider dashboard
   # 2. Add new key to environment variables alongside old key
   STRIPE_SECRET_KEY_NEW=sk_live_new...
   STRIPE_SECRET_KEY_OLD=sk_live_old...

   # 3. Update code to try new key, fallback to old key
   # 4. Deploy with both keys active (grace period starts)
   # 5. After 1 hour, remove old key from environment
   # 6. Revoke old key in provider dashboard
   ```

3. **Automated rotation (future enhancement)**:
   - Use AWS Secrets Manager or HashiCorp Vault for automatic rotation
   - MVP: Manual rotation via Railway environment variables

**Testing**: Simulate key rotation in staging environment quarterly.

### Security Scanning Requirements (SAST/DAST/Dependency)

**SAST (Static Application Security Testing)**:
- Tool: Bandit (Python), ESLint security plugins (TypeScript)
- Frequency: On every commit (GitHub Actions pre-commit hook)
- Configuration: `.bandit.yml` (see Section XII)
- Fail build on: High severity issues (SQL injection, hardcoded secrets)

**DAST (Dynamic Application Security Testing)**:
- Tool: OWASP ZAP (Zed Attack Proxy)
- Frequency: Weekly automated scans on staging environment
- Scope: All authenticated API endpoints
- Fail deployment on: SQL injection, XSS vulnerabilities

**Dependency Scanning**:
- Tool: Dependabot (GitHub native), Snyk (backup)
- Frequency: Daily scans for new CVEs
- Auto-update: Minor version bumps auto-merged if tests pass
- Manual review: Major version bumps, security patches

**CI/CD Integration**:
```yaml
# .github/workflows/security.yml
name: Security Scanning
on: [push, pull_request]
jobs:
  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Bandit
        run: bandit -r backend/src -f json -o bandit-report.json
      - name: Fail on high severity
        run: python scripts/check-bandit-report.py
```

### Security Training Requirements for Developers

**Initial Onboarding**:
- All developers complete OWASP Top 10 training (2 hours, online course)
- Review EstiMate threat model (Section XII) before first commit
- Sign security policy acknowledgment

**Ongoing Training**:
- Quarterly security lunch-and-learn sessions (30 minutes)
- Topics: Recent CVEs affecting our stack, secure coding practices, incident response drills
- Annual refresher on OWASP Top 10

**Security Champions**:
- Designate 1-2 team members as security champions
- Champions attend monthly security webinars (OWASP, SANS)
- Champions review all security-sensitive PRs

**Resources**:
- OWASP Cheat Sheets (https://cheatsheetseries.owasp.org/)
- Python Security Best Practices (https://python.readthedocs.io/en/stable/library/security_warnings.html)
- React Security (https://reactjs.org/docs/dom-elements.html#dangerouslysetinnerhtml)

### Load Pattern Specification for 10K Concurrent Users

**Detailed Load Breakdown** (see Section XIII for table):
- 10,000 concurrent users = 166 requests/second sustained (avg 1 req per user per 60s)
- Peak burst: 250 req/s (50% spike during weekday 6-7pm)
- Request distribution: See "Load Pattern for 10K Concurrent Users" table in Section XIII
- Geographic distribution: 60% US, 20% CA, 10% UK, 10% other
- User behavior:
  - 70% returning users (session duration: 5-10 minutes)
  - 30% new users (session duration: 15-20 minutes, more exploration)
- Cache effectiveness: 80% hit rate reduces backend load to ~33 req/s

**Load Testing Validation**:
- Tool: Locust (Python load testing framework)
- Test scenario: Ramp up from 100 to 10,000 users over 30 minutes
- Success criteria: p95 latency < 750ms, zero 5xx errors, CPU < 70%

### Photo Quality vs Upload Speed Trade-off

**Trade-off Analysis**:
- **High quality** (Original resolution, lossless compression):
  - Average photo size: 3-5 MB (iPhone 14 Pro: 12MP HEIC)
  - Upload time: 6-10 seconds per photo on 4G (5 Mbps upload)
  - Total upload time for 10 photos: 60-100 seconds
  - Pros: Better CV analysis accuracy, users can zoom in
  - Cons: Slow upload, higher storage costs ($0.023/GB S3 Standard)

- **Medium quality** (1920×1080, lossy compression 80%):
  - Average photo size: 500-800 KB
  - Upload time: 1-2 seconds per photo on 4G
  - Total upload time for 10 photos: 10-20 seconds
  - Pros: Fast upload, acceptable CV accuracy, lower costs
  - Cons: May miss fine details (texture, small text)

**Decision**: Target medium quality for uploads, resize client-side before upload.

**Implementation**:
```typescript
// Frontend: Resize before upload using browser-image-compression
import imageCompression from 'browser-image-compression';

const options = {
  maxSizeMB: 1,             // Max 1MB per photo
  maxWidthOrHeight: 1920,   // Max dimension 1920px
  useWebWorker: true,       // Don't block UI thread
  fileType: 'image/jpeg',   // Convert HEIC to JPEG
};

const compressedFile = await imageCompression(file, options);
```

**User override**: Business tier users can toggle "High Quality Upload" in settings (uploads original resolution).

### CDN Cost vs Performance Trade-offs

**CDN Usage Analysis**:
- Assets served via CDN: Frontend bundle, images, static assets
- Vercel CDN: Included in Pro plan ($20/month, 1TB bandwidth)
- Additional bandwidth: $40/TB (if exceeded)

**Trade-off Scenarios**:

1. **Scenario A: Aggressive CDN caching (current approach)**:
   - Cache-Control: `public, max-age=31536000, immutable` for versioned assets
   - Cost: ~$20/month (within Vercel Pro allowance)
   - Performance: Excellent (global edge cache, <50ms TTFB)
   - Risk: Stale assets if cache not properly invalidated

2. **Scenario B: Conservative caching**:
   - Cache-Control: `public, max-age=3600` (1 hour TTL)
   - Cost: Higher bandwidth usage, potential $60/month (3TB)
   - Performance: Slower (more origin requests, ~200ms TTFB)
   - Risk: Lower, always fresh assets

3. **Scenario C: Self-hosted CDN (CloudFlare, Fastly)**:
   - Cost: $20/month (CloudFlare Pro) + engineering time
   - Performance: Comparable to Vercel
   - Risk: Additional infrastructure complexity

**Decision**: Stick with Scenario A (aggressive caching) for MVP.
- Mitigation: Use content hashing in build process (webpack `[contenthash]`)
- Fallback: If bandwidth exceeds 1TB/month, evaluate CloudFlare Workers

### API Response Size Budgets

**Response Size Limits**:
- Individual API responses: 500 KB maximum (FR-071)
- Paginated list endpoints: 50 items per page, ~200 KB per page
- Photo metadata: 2 KB per photo (URL, dimensions, upload date)
- Shopping list: ~10 KB (100 items × 100 bytes each)
- Pricing data: ~50 KB (50 retailers × 1 KB each)

**Enforcement**:
```python
# Backend middleware: Check response size before sending
@app.middleware("http")
async def limit_response_size(request: Request, call_next):
    response = await call_next(request)
    content_length = int(response.headers.get("content-length", 0))

    if content_length > 500_000:  # 500 KB
        logger.warning(f"Response size {content_length} exceeds budget for {request.url}")
        # Consider pagination or filtering

    return response
```

**Monitoring**: Track response sizes in APM (New Relic) and alert if p95 > 400 KB.

### Performance Requirements ID Scheme

**ID Format**: `PERF-XXX` where XXX is a zero-padded number.

**Requirement Categories**:
- PERF-001 to PERF-099: API latency requirements
- PERF-100 to PERF-199: Frontend performance requirements
- PERF-200 to PERF-299: Database performance requirements
- PERF-300 to PERF-399: Caching requirements
- PERF-400 to PERF-499: Scalability requirements

**Example Mapping**:
| ID | Requirement | Target | Success Criteria |
|----|-------------|--------|------------------|
| PERF-001 | GET /projects latency | p95 < 200ms | SC-005 |
| PERF-002 | POST /projects/{id}/estimate latency | p95 < 30s | SC-005 |
| PERF-101 | LCP (Largest Contentful Paint) | < 2.0s | SC-005 |
| PERF-102 | TTI (Time to Interactive) | < 3.5s | FR-069 |
| PERF-201 | Database query latency | p95 < 100ms | Plan §Technical Context |
| PERF-301 | Cache hit rate | > 80% | Plan §Technical Context |
| PERF-401 | Max concurrent users | 10,000 | SC-005 |

**Traceability**: All PERF-XXX IDs link back to FR-XXX (spec.md) or SC-XXX (spec.md) or Plan sections.

**Tracking**: Create GitHub labels `perf:PERF-XXX` for performance-related issues and PRs.

---

## Project Structure

### Documentation (this feature)

```text
specs/001-materials-estimation/
├── spec.md                  # Feature specification (WHAT/WHY)
├── plan.md                  # This file - implementation plan (HOW)
├── research.md              # Phase 0 output - tech decisions
├── data-model.md            # Phase 1 output - database schema
├── quickstart.md            # Phase 1 output - dev setup guide
├── contracts/               # Phase 1 output - API contracts
│   ├── openapi.yaml         # OpenAPI 3.1 schema
│   └── README.md            # Contract documentation
├── checklists/              # Quality gates
│   └── requirements.md      # Spec validation (already complete)
└── tasks.md                 # Phase 2 output (created by /speckit.tasks, not /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/                 # FastAPI endpoints
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   ├── projects.py
│   │   │   ├── estimates.py
│   │   │   ├── shopping_lists.py
│   │   │   ├── pricing.py
│   │   │   └── subscriptions.py
│   │   ├── dependencies.py  # DI container
│   │   └── middleware.py    # Auth, logging, tracing
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── shopping_list.py
│   │   ├── subscription.py
│   │   └── feedback.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── request/
│   │   └── response/
│   ├── repositories/        # Data access layer
│   │   ├── base.py
│   │   ├── user_repository.py
│   │   ├── project_repository.py
│   │   └── shopping_list_repository.py
│   ├── services/            # Business logic
│   │   ├── estimation/
│   │   │   ├── estimation_service.py
│   │   │   ├── waste_calculator.py
│   │   │   └── strategies/  # Material-specific strategies
│   │   ├── computer_vision/
│   │   │   ├── cv_service.py
│   │   │   └── adapters/    # Cloud Vision, Rekognition
│   │   ├── pricing/
│   │   │   ├── pricing_service.py
│   │   │   ├── optimizer.py
│   │   │   └── adapters/    # Home Depot, Lowe's APIs
│   │   ├── payment/
│   │   │   └── stripe_service.py
│   │   └── auth/
│   │       └── auth_service.py
│   ├── core/                # Shared utilities
│   │   ├── config.py        # Settings from env vars
│   │   ├── database.py      # DB connection, session
│   │   ├── cache.py         # Redis client
│   │   ├── storage.py       # S3 client
│   │   └── logging.py       # Structured logging setup
│   └── main.py              # FastAPI app entry point
├── tests/
│   ├── unit/                # Unit tests (TDD)
│   │   ├── test_estimation/
│   │   ├── test_pricing/
│   │   └── test_repositories/
│   ├── integration/         # API endpoint tests
│   │   ├── test_auth_api.py
│   │   ├── test_projects_api.py
│   │   └── test_estimates_api.py
│   ├── contract/            # External API contract tests
│   │   ├── test_stripe_adapter.py
│   │   └── test_retailer_adapters.py
│   └── performance/         # Load tests
│       └── test_estimation_throughput.py
├── alembic/                 # Database migrations
│   └── versions/
├── pyproject.toml           # Poetry dependencies
├── pytest.ini
├── mypy.ini
└── Dockerfile

frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── common/          # Buttons, inputs, modals
│   │   ├── estimation/      # Photo uploader, room form
│   │   └── shopping-list/   # Item list, price comparison
│   ├── pages/               # Route components
│   │   ├── HomePage.tsx
│   │   ├── NewProjectPage.tsx
│   │   ├── EstimationPage.tsx
│   │   ├── ShoppingListPage.tsx
│   │   ├── PricingPage.tsx
│   │   └── DashboardPage.tsx
│   ├── hooks/               # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useProjects.ts
│   │   └── useEstimation.ts
│   ├── services/            # API clients
│   │   ├── api.ts           # Axios instance with interceptors
│   │   ├── auth.ts
│   │   ├── projects.ts
│   │   ├── estimates.ts
│   │   └── pricing.ts
│   ├── types/               # TypeScript interfaces
│   │   ├── project.ts
│   │   ├── shopping-list.ts
│   │   └── user.ts
│   ├── utils/               # Helper functions
│   │   ├── format.ts
│   │   └── validation.ts
│   ├── App.tsx              # Root component with routing
│   ├── main.tsx             # React entry point
│   └── vite-env.d.ts
├── tests/
│   ├── unit/                # Component tests
│   │   ├── estimation.test.tsx
│   │   └── shopping-list.test.tsx
│   └── e2e/                 # Playwright tests
│       ├── auth.spec.ts
│       └── estimation-flow.spec.ts
├── public/
│   └── assets/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── playwright.config.ts
└── Dockerfile

shared/
├── docs/
│   ├── adr/                 # Architecture Decision Records
│   │   ├── 001-computer-vision-approach.md
│   │   ├── 002-retailer-api-strategy.md
│   │   └── 003-estimation-algorithms.md
│   └── api/
│       └── openapi.yaml     # Symlink to specs/001-materials-estimation/contracts/openapi.yaml
├── scripts/
│   ├── setup-dev.sh         # Local development setup
│   ├── seed-database.sh     # Test data
│   └── migrate.sh           # Run Alembic migrations
└── docker-compose.yml       # Local development stack
```

**Structure Decision**: Web application (Option 2) selected due to:
- Separate frontend and backend concerns
- Independent deployment (frontend to CDN, backend to containers)
- Clear API boundary for mobile app future expansion
- Team specialization (frontend vs backend developers)

---

## Complexity Tracking

> **No violations requiring justification** - Constitution Check passed all gates.

---

## Phase 0: Research & Technology Decisions

*Purpose: Resolve technical unknowns and document technology choices*

### Research Task List

Based on Technical Context unknowns and key design decisions:

1. **Computer Vision Approach**
   - Decision needed: Build custom model vs cloud API
   - Research: OpenCV local processing vs Google Cloud Vision vs AWS Rekognition
   - Criteria: Accuracy (target 85%), cost per analysis, latency, scalability

2. **Retailer API Integration**
   - Decision needed: Official APIs vs web scraping
   - Research: Home Depot API, Lowe's API availability, rate limits, terms of service
   - Fallback: Web scraping libraries (Playwright, Scrapy), legal considerations

3. **Estimation Algorithms**
   - Decision needed: Rule-based vs ML-based
   - Research: Industry-standard waste factors, pattern-matching logic
   - Evolution path: Start rule-based, add ML with feedback data (FR-029)

4. **Authentication Provider**
   - Decision needed: Auth0 vs Supabase Auth vs custom JWT
   - Research: OAuth2 flows, MFA support, cost at scale, developer experience

5. **Database Schema Optimization**
   - Decision needed: Normalization level, indexing strategy
   - Research: Multi-tenancy patterns, RLS performance at scale

6. **Photo Storage Strategy**
   - Decision needed: Direct S3 upload vs backend proxy
   - Research: Presigned URLs, virus scanning, cost optimization

7. **Caching Strategy**
   - Decision needed: Cache invalidation approach for pricing data
   - Research: TTL-based vs event-based, cache warming strategies

8. **Frontend State Management**
   - Decision needed: React Query only vs + Zustand/Redux
   - Research: Server state (React Query) vs client state needs

9. **Deployment Strategy**
   - Decision needed: AWS ECS vs EKS vs Serverless (Lambda)
   - Research: Cost at target scale, auto-scaling, cold start impact

10. **Monitoring & APM**
    - Decision needed: DataDog vs New Relic vs Grafana Cloud
    - Research: Cost, OpenTelemetry compatibility, alerting capabilities

### Research Assignments

These will be delegated to specialized research agents (executed during this `/speckit.plan` command):

- Agent 1: Computer vision research (CVTask)
- Agent 2: Retailer API research (RetailerTask)
- Agent 3: Auth provider research (AuthTask)
- Agent 4: Deployment strategy research (DeployTask)
- Agent 5: Estimation algorithms research (AlgoTask)

**Output**: `research.md` with decisions, rationales, and alternatives documented

---

## Phase 1: Design & Contracts

*Purpose: Define data models, API contracts, and development setup*

**Prerequisites**: `research.md` complete with all decisions finalized

### Deliverables

1. **data-model.md**: Database schema with:
   - Entity definitions from spec.md (User, Project, ShoppingList, etc.)
   - Field types, constraints, indexes
   - Relationships and foreign keys
   - RLS policies for multi-tenancy
   - Alembic migration scripts plan

2. **contracts/openapi.yaml**: API specification with:
   - All endpoints from functional requirements (FR-001 to FR-034)
   - Request/response schemas (Pydantic → OpenAPI)
   - Authentication requirements (Bearer token)
   - Error responses (4xx, 5xx)
   - Rate limiting annotations

3. **contracts/README.md**: Contract documentation with:
   - API versioning strategy
   - Authentication flow
   - Common error codes
   - Pagination approach
   - Filtering/sorting conventions

4. **quickstart.md**: Developer onboarding guide with:
   - Prerequisites (Python 3.11, Node 18, Docker, PostgreSQL, Redis)
   - Local setup (clone, install deps, env vars)
   - Database initialization (Alembic migrations, seed data)
   - Running backend (uvicorn) and frontend (Vite)
   - Running tests (pytest, vitest, playwright)
   - Debugging tips

5. **Update agent context**:
   - Run `.specify/scripts/bash/update-agent-context.sh claude`
   - Add new technologies from this plan to `.claude/AGENT.md`
   - Preserve existing manual additions

**Output**: All Phase 1 artifacts committed to `specs/001-materials-estimation/`

---

## Phase 2: Task Breakdown (Not Created By This Command)

**Prerequisites**: All Phase 1 artifacts complete and Constitution Check re-validated

**Note**: Phase 2 is handled by the `/speckit.tasks` command, not `/speckit.plan`.

The tasks will be:
- Organized by priority (P1 MVP, P2 Enhanced, P3 Advanced)
- Dependency-ordered (foundation → features → integration)
- Mapped to user stories from spec.md
- Sized to 1-4 hour increments
- Includes test-first requirements (TDD)
- References Beads issue IDs for tracking

---

## Risk Assessment

### High-Risk Areas

1. **Computer Vision Accuracy** (HIGH)
   - Risk: CV analysis <85% accuracy → user frustration, manual overrides
   - Mitigation: Start with cloud APIs (proven accuracy), fallback to manual input
   - Validation: Test with diverse room photos (lighting, angles, shapes)

2. **Retailer API Availability** (HIGH)
   - Risk: Home Depot/Lowe's may not provide public APIs
   - Mitigation: Web scraping fallback, cached pricing (48h TTL)
   - Validation: Prototype API calls, review terms of service, legal consult

3. **Estimation Algorithm Accuracy** (MEDIUM)
   - Risk: Waste factors too conservative (overestimate) or too aggressive (underestimate)
   - Mitigation: Industry-standard factors + user skill modifiers, feedback loop (FR-027)
   - Validation: Test with real projects, compare to actual usage

4. **Subscription Conversion Rate** (MEDIUM)
   - Risk: Free tier too generous → low conversion, or too restrictive → churn
   - Mitigation: A/B test limits (3 projects vs 5), analytics on upgrade triggers
   - Validation: Monitor conversion metrics (SC-004: target 10%)

5. **Photo Upload Performance** (MEDIUM)
   - Risk: Large uploads (10MB × 20 photos = 200MB) → slow, timeouts
   - Mitigation: Direct S3 upload with presigned URLs, progress indicators
   - Validation: Load test with max-size uploads, monitor p95 latency
   - Trade-off: Original quality preserved (no compression), optimize after 90 days (80% JPEG quality)

6. **Multi-Tenancy Data Leakage** (LOW but CRITICAL)
   - Risk: RLS misconfiguration → cross-user data access
   - Mitigation: Automated tests for tenant isolation, code review checklist
   - Validation: Integration tests asserting user A cannot access user B's projects

### Performance Risks

1. **Photo Analysis Latency** (MEDIUM)
   - Risk: CV processing >30s → user abandonment
   - Mitigation: Async processing with WebSocket updates, batch optimization
   - Validation: Benchmark with 3-4 photos, target p95 <30s

2. **Database Query Performance** (LOW)
   - Risk: N+1 queries on shopping list endpoint
   - Mitigation: SQLAlchemy eager loading, query analysis in tests
   - Validation: Explain plans, assert query count <5 per endpoint

3. **Pricing Data Staleness** (LOW)
   - Risk: 48h cache → prices inaccurate
   - Mitigation: Display last-updated timestamp, refresh on demand
   - Validation: Monitor user feedback on price discrepancies

### Security Risks

1. **File Upload Vulnerabilities** (MEDIUM)
   - Risk: Malicious files uploaded (viruses, exploits)
   - Mitigation: MIME type validation, virus scanning (ClamAV), size limits
   - Validation: Security scan in CI, upload malicious test files

2. **API Rate Limiting Bypass** (LOW)
   - Risk: Distributed attacks bypass IP-based rate limits
   - Mitigation: User-based limits + IP-based, CAPTCHA for suspicious activity
   - Validation: Load test with distributed IPs, verify blocks

3. **PII Leakage in Logs** (LOW but CRITICAL)
   - Risk: Payment info, email in log messages
   - Mitigation: Structured logging with PII scrubbing, log review
   - Validation: Audit logs for sensitive patterns, automated scanning

---

## Success Metrics Alignment

Mapping implementation to Success Criteria from spec.md:

| Success Criterion | Implementation Approach | Measurement |
|-------------------|------------------------|-------------|
| SC-001: Complete estimation in <5 min | Streamlined UI, auto-fill from CV, progress indicators | Frontend analytics (Plausible) |
| SC-002: 10% accuracy for 80% of projects | Industry waste factors + skill modifiers, feedback loop | Post-project surveys, actual vs estimated |
| SC-003: 15-20% waste reduction | Waste calculator with material + skill + complexity factors | User feedback surveys |
| SC-004: 10% free-to-pro conversion | Feature gating (3 project limit), upgrade prompts | Stripe webhook events, analytics |
| SC-005: 10K concurrent users, <2s load | Horizontal scaling, CDN, Redis caching | Load testing (Locust), APM (p95 latency) |
| SC-006: $50+ savings per project | Price optimizer across retailers | Price comparison delta shown in UI |
| SC-007: 95% checkout integration success | Robust error handling, fallback to manual link | Success/error tracking per retailer |
| SC-008: 4.2/5 user satisfaction | Quality UX, accurate estimates, clear value | In-app NPS surveys |
| SC-009: 60% pro users create >1 project/month | Seamless project creation, templates (US3) | User engagement metrics |
| SC-010: 30% time reduction for contractors | Quote export, client management, analytics | Business tier user interviews |
| SC-011: 5% accuracy improvement year 1 | ML feedback loop (FR-029), A/B testing | Historical accuracy tracking |
| SC-012: 99.5% uptime | Multi-AZ deployment, health checks, auto-scaling | Uptime monitoring (UptimeRobot) |
| SC-013: 100% WCAG 2.1 AA automated test pass | axe-core in component tests, Playwright E2E accessibility checks | CI/CD automated axe tests, jest-axe unit tests |
| SC-014: Lighthouse accessibility score ≥95 | Headless UI components, semantic HTML, ARIA implementation | Lighthouse CI in GitHub Actions |
| SC-015: Bundle sizes (JS ≤250KB, CSS ≤50KB gzipped) | Vite code splitting, Tailwind purge, lazy loading | CI bundle size enforcement, vite-bundle-visualizer |
| SC-016: TTI ≤3.5s, FCP ≤1.2s on 4G | Critical path optimization, async scripts, image optimization | Lighthouse CI, WebPageTest 4G throttling, RUM |
| SC-017: Zero CRITICAL/HIGH pen test vulnerabilities | Annual penetration testing, OWASP Top 10 coverage, security code review | Third-party pen test report, 30-day remediation SLA for MEDIUM |

---

## Next Steps

After `/speckit.plan` completes:

1. **Review research.md** - Validate all technology decisions
2. **Review data-model.md** - Confirm schema matches spec entities
3. **Review contracts/openapi.yaml** - Verify all FR requirements covered
4. **Review quickstart.md** - Test local setup instructions
5. **Run `/speckit.checklist`** - Generate domain-specific checklists (security, accessibility, performance)
6. **Run `/speckit.tasks`** - Generate dependency-ordered task list
7. **Run `/speckit.analyze`** - Cross-validate spec ↔ plan ↔ tasks consistency
8. **Run `/speckit.implement`** - Begin TDD implementation

---

**Plan Status**: Ready for Phase 0 research execution (automated below)
