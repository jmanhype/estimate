# Technology Research & Decisions

**Feature**: EstiMate - AI Materials Estimation
**Date**: 2025-11-30
**Purpose**: Document technology choices, rationales, and alternatives for implementation

---

## Decision 1: Computer Vision Approach

**Decision**: Start with Google Cloud Vision API, with AWS Rekognition as failover

**Rationale**:
- **Accuracy**: Cloud Vision API proven 85%+ accuracy for object/space detection
- **Speed to market**: No model training required, immediate availability
- **Cost**: ~$1.50 per 1000 images (first 1000/month free), acceptable at target scale
  - Est. 5M photos year 1 = ~$7,500/year for CV
- **Latency**: <5s per image analysis (well under 30s target for 3-4 photos)
- **Scalability**: Managed service, no infrastructure management
- **Fallback**: AWS Rekognition as secondary ($1.00 per 1000 images) if GCV unavailable
- **Manual override**: Always available if both APIs fail

**Alternatives Considered**:
1. **Custom OpenCV + ML model**:
   - Pros: Lower per-image cost at scale, full control
   - Cons: Requires training data (don't have yet), 2-3 month development time, uncertain accuracy
   - Rejected: Not viable for MVP, revisit after 100K+ photos collected

2. **Local OpenCV processing (no ML)**:
   - Pros: Free, no API dependencies
   - Cons: Limited to basic dimension extraction, 60-70% accuracy, requires user correction
   - Rejected: Accuracy too low to meet 85% target

**Implementation Notes**:
- Use Google Cloud Vision API's `OBJECT_LOCALIZATION` and `IMAGE_PROPERTIES` features
- Extract room boundaries, wall detection, door/window identification
- Store raw API responses for future model training
- Implement circuit breaker pattern: 3 consecutive failures → fallback chain
- Cache CV results in Redis (key: SHA256 of image)

**Migration Path**:
- Phase 1 (MVP): Cloud Vision API only
- Phase 2 (after 100K photos): Evaluate custom model training
- Phase 3 (if cost >$50K/year): Hybrid approach (custom for common cases, cloud for edge cases)

---

## Decision 2: Retailer API Integration

**Decision**: Web scraping with Playwright + fallback to manual linking

**Rationale**:
- **API Availability Research**:
  - **Home Depot**: No public API documented (as of 2025-11-30)
  - **Lowe's**: No public API for product pricing (only B2B catalog API)
  - **Third-party**: Some unofficial APIs exist but violate ToS
- **Web Scraping Legality**: Legal for public pricing data (established precedent in US case law) as long as:
  - Respect robots.txt
  - Rate limit requests (no more than 1 req/10s per retailer)
  - Don't create excessive load
  - Public data only (no login required)
- **Cost**: Free (compute cost only)
- **Maintenance**: Scraper updates needed when retailers change markup (est. 2-4 times/year)

**Alternatives Considered**:
1. **Official APIs**:
   - Pros: Stable, supported, ToS-compliant
   - Cons: Not available for pricing data
   - Status: Monitor for future availability

2. **Affiliate Networks** (ShareASale, CJ):
   - Pros: Product data feeds available, earn commission
   - Cons: Pricing data often stale (updated weekly), limited to affiliate-participating products
   - Rejected: 48h freshness requirement not met

3. **Manual links only** (no price comparison):
   - Pros: No scraping maintenance
   - Cons: No price comparison feature (SC-006 savings metric unfulfilled)
   - Rejected: Core value prop requires price comparison

**Implementation Notes**:
- Use Playwright (headless Chromium) for dynamic content rendering
- Scraping schedule: Every 48 hours, batch processing overnight
- Store pricing in PostgreSQL `retailer_prices` table with `last_updated` timestamp
- Cache in Redis with 48h TTL
- Error handling: If scraper fails, use stale data up to 7 days with disclaimer
- Fallback: If no pricing available, show "Check price at [Retailer]" button with direct link

**Scraping Strategy**:
- Target product detail pages (predictable structure)
- Selector hierarchy: data attributes → classes → structure
- Change detection: Hash HTML structure, alert on changes
- Rate limiting: 1 request per 10 seconds per retailer
- User-Agent: Identify as "EstiMate Price Comparison Bot" with contact email

**Legal Compliance**:
- Consult with legal counsel before launch
- Add "Prices provided for comparison purposes, verify at retailer" disclaimer
- No circumvention of paywalls or authentication
- Respect robots.txt and meta robots tags

**Migration Path**:
- MVP: Scrape Home Depot + Lowe's only
- Phase 2: Add Menards, Ace Hardware based on user requests
- Future: If official APIs become available, migrate immediately

---

## Decision 3: Estimation Algorithms

**Decision**: Rule-based algorithms with skill/material/complexity factors, evolve to ML with feedback data

**Rationale**:
- **Industry Standards Available**: Well-documented waste factors exist
  - Paint: 5-10% (flat surfaces) to 15-20% (textured, high ceilings)
  - Flooring: 10% (straight layout) to 20% (diagonal, pattern matching)
  - Tile: 10% (simple) to 25% (complex patterns, cuts)
  - Lumber: 5% (experienced) to 15% (beginner)
- **Deterministic & Testable**: Rule-based easier to validate and debug
- **Immediate Availability**: No training data required for MVP
- **Clear Value**: Still achieves 15-20% waste reduction vs "buy extra"

**Rule-Based Algorithm Structure**:
```
Estimated Quantity = Base Calculation × (1 + Waste Factor)

Waste Factor = Material Base Rate
             × Skill Level Multiplier
             × Complexity Multiplier

Skill Multipliers:
- Expert: 0.5 (reduce waste by half)
- Intermediate: 1.0 (standard rate)
- Beginner: 1.5 (increase waste buffer)

Complexity Multipliers (CV-detected):
- Rectangular room, no obstacles: 1.0
- Irregular shape OR obstacles: 1.2
- Irregular shape AND obstacles: 1.4
- High ceilings (>10ft) OR vaulted: 1.3
```

**Material-Specific Calculations**:

1. **Paint**:
   - Base: (Wall Area - (Doors × 20sqft) - (Windows × 15sqft)) / Coverage per Gallon
   - Coverage: 350 sqft/gallon (standard), 250 sqft/gallon (textured)
   - Base Waste: 10%
   - Rounds up to full gallons

2. **Flooring (planks/tiles)**:
   - Base: Room Area sqft
   - Base Waste: 10% (standard) + 10% (pattern matching if applicable)
   - Converts to boxes based on coverage per box

3. **Tile**:
   - Base: Area sqft / Tile Size
   - Base Waste: 15% (standard) + additional for diagonal, mosaics
   - Related materials: Grout (1 bag per 100 sqft), Thinset (calculated)

4. **Lumber/Decking**:
   - Base: Linear feet needed
   - Base Waste: 10% for cuts, warping, defects
   - Rounds up to sellable lengths (8ft, 10ft, 12ft, 16ft)

**Alternatives Considered**:
1. **ML-based from start**:
   - Pros: Could be more accurate with enough data
   - Cons: No training data available, black box harder to debug
   - Rejected: Not viable for MVP

2. **Simple area calculation only** (no waste):
   - Pros: Simplest implementation
   - Cons: Underestimates, defeats waste reduction value prop
   - Rejected: Users would run out of materials

**Implementation Notes**:
- Implement as Strategy pattern per material type
- Store calculation metadata with each estimate (factors used, CV confidence)
- A/B test waste factors during beta (10% vs 15% for paint) to optimize
- Log all estimates for future ML training data

**Evolution to ML** (post-launch, after feedback data):
- Collect actual usage data via FR-027 (feedback)
- Train regression model: `Actual Usage = f(Room Dimensions, Material, Skill, Complexity, Seasonal Factors)`
- Use ML predictions to adjust rule-based factors dynamically
- Start with paint (most feedback expected), expand to other materials
- Always show "Based on N similar projects" when ML-adjusted

---

## Decision 4: Authentication Provider

**Decision**: Supabase Auth (managed Auth0 alternative)

**Rationale**:
- **Cost**: Free tier: 50K monthly active users (MAU), then $0.00325/MAU
  - Year 1 est. 100K users × 20% active = 20K MAU = FREE
  - Auth0: $240/month minimum for production, too expensive for early stage
- **Features**:
  - ✅ OAuth2/OIDC (Google, GitHub, email)
  - ✅ JWT tokens (compatible with FastAPI)
  - ✅ MFA support (TOTP, SMS)
  - ✅ Row-Level Security policies (Supabase integrates with PostgreSQL RLS)
  - ✅ Email templates, magic links
- **Integration**: Supabase provides PostgreSQL + Auth + Storage (S3-compatible)
  - Can use Supabase for database AND auth (simplifies stack)
- **Developer Experience**: Excellent docs, client SDKs for Python & JS
- **Scalability**: Proven at 100K+ MAU, auto-scaling

**Alternatives Considered**:
1. **Auth0**:
   - Pros: Industry standard, robust features, extensive integrations
   - Cons: $240/month minimum ($2,880/year), expensive for early stage
   - Rejected: Cost too high pre-revenue

2. **Custom JWT implementation**:
   - Pros: Full control, no external dependency
   - Cons: Security burden (password hashing, token refresh, email verification), ongoing maintenance
   - Rejected: Not core competency, security risk

3. **Firebase Auth**:
   - Pros: Free tier generous (10K MAU), good features
   - Cons: Google lock-in, less control, doesn't integrate with PostgreSQL RLS
   - Rejected: Prefer PostgreSQL-native solution

**Implementation Notes**:
- Use Supabase JS client for frontend (social logins, magic links)
- Use Supabase Python client for backend (verify JWTs, session management)
- Store user metadata in own PostgreSQL `users` table (synced via Supabase webhooks)
- Enable MFA for Business tier users (enforce via subscription check)
- Configure RLS policies to enforce user_id filtering on all tables

**Auth Flow**:
1. Frontend: User clicks "Sign in with Google" → Supabase handles OAuth
2. Supabase returns JWT (contains user_id, email, role)
3. Frontend stores JWT in httpOnly cookie + localStorage
4. Backend: FastAPI middleware verifies JWT on each request → extracts user_id
5. Database: RLS policies automatically filter queries by `auth.uid()` (Supabase function)

**Migration Path**:
- MVP: Email/password + Google OAuth
- Phase 2: Add GitHub, Microsoft OAuth based on demand
- Phase 3: Enterprise SSO (SAML) if large contractors require it (via Auth0 migration)

---

## Decision 5: Database Schema Optimization

**Decision**: Normalized schema with strategic denormalization for pricing data, RLS policies for all tables

**Rationale**:
- **Multi-Tenancy**: RLS provides secure, automatic user_id filtering
- **Normalization**: Prevent data anomalies, easier to maintain
- **Denormalization**: Pricing data duplicated in `shopping_list_items` to preserve historical prices
  - User needs to see original estimate even if retailer prices change
  - Alternative (join to current prices) would show different values over time
- **Indexing**: All foreign keys indexed, composite indexes for common queries

**Schema Highlights**:
- `users`: Managed by Supabase Auth, extended with `skill_level`, `subscription_tier`
- `projects`: Belongs to user, has photos, timeline, shopping list
- `shopping_lists`: One per project, has line items
- `shopping_list_items`: Denormalized with `estimated_cost` snapshot
- `retailer_prices`: Separate table, joined for current prices, not historical

**RLS Policies** (enforced at database level):
```sql
-- All tables with user_id column
CREATE POLICY "Users can only access their own data"
ON table_name FOR ALL
USING (user_id = auth.uid());

-- Business tier users can access shared projects (future)
CREATE POLICY "Business users can access shared projects"
ON projects FOR SELECT
USING (
  user_id = auth.uid()
  OR id IN (
    SELECT project_id FROM project_shares
    WHERE shared_with_user_id = auth.uid()
  )
);
```

**Indexes**:
- Primary keys (auto-indexed)
- Foreign keys: `user_id`, `project_id`, `shopping_list_id`
- Queries: `(user_id, created_at)` for dashboard "recent projects"
- Search: `material_name` GIN index for fuzzy search (future)

**Alternatives Considered**:
1. **Full denormalization** (NoSQL-style):
   - Pros: Fewer joins, faster reads
   - Cons: Data duplication, update anomalies, harder to query
   - Rejected: Relational structure fits data model well

2. **Application-level multi-tenancy** (no RLS):
   - Pros: More control, easier to debug
   - Cons: Security risk (one missed WHERE clause = data leak), verbose code
   - Rejected: RLS is stronger security guarantee

**Implementation Notes**:
- Use Alembic for migrations (version control for schema)
- Enable `FORCE ROW LEVEL SECURITY` on all tables
- Test tenant isolation in integration tests (user A cannot access user B's data)
- Monitor RLS performance at scale (RLS adds overhead, may need query optimization)

---

## Decision 6: Photo Storage Strategy

**Decision**: Direct S3 upload via presigned URLs, with backend-triggered virus scanning

**Rationale**:
- **Performance**: Client uploads directly to S3, bypasses backend bottleneck
  - 200MB max (20 photos × 10MB) → 30s upload @ 5 Mbps (typical home internet)
  - Backend proxy would double time (client → backend → S3)
- **Cost**: S3 Standard: $0.023/GB/month storage, $0.09/GB transfer out
  - 5M photos/year × 2MB avg = 10TB = $230/month storage, $900/month egress (CDN reduces this)
- **Security**: Presigned URLs time-limited (15 min), scoped to user's directory
- **Virus Scanning**: Lambda function triggered on S3 upload, uses ClamAV
  - Scans file, quarantines if malicious, updates database status

**Presigned URL Flow**:
1. Frontend: Request upload URL from `/api/v1/projects/{id}/photos/upload-url`
2. Backend: Generate presigned S3 PUT URL, expires in 15 minutes
   - Key: `{user_id}/{project_id}/{photo_id}_{timestamp}.jpg`
   - Content-Type: Restrict to `image/jpeg`, `image/png`, `image/heic`
   - Content-Length: Max 10MB
3. Frontend: PUT file directly to S3 using presigned URL
4. S3 Event: Triggers Lambda virus scan
5. Lambda: ClamAV scan → quarantine if malicious, set `scan_status` in DB
6. Backend: Poll scan status before allowing CV analysis

**Alternatives Considered**:
1. **Backend proxy upload**:
   - Pros: Simpler virus scanning (scan before S3)
   - Cons: Backend becomes bottleneck, RAM usage for large files
   - Rejected: Doesn't scale to 10K concurrent users

2. **Supabase Storage** (S3-compatible):
   - Pros: Integrated with Supabase Auth, automatic RLS
   - Cons: More expensive ($0.10/GB vs S3's $0.023/GB), less control
   - Reconsidered: Use Supabase Storage for MVP (simpler), migrate to S3 if cost >$500/month

**Implementation Notes**:
- Use Supabase Storage for MVP (integrated auth, simpler setup)
- Migrate to S3 + CloudFront if storage costs exceed $500/month
- Virus scanning: Supabase has edge functions for scanning (ClamAV)
- CDN: CloudFront (or Supabase CDN) for photo delivery, cache photos for 30 days
- Cleanup: Delete photos after project deletion, or after 2 years (GDPR compliance)

---

## Decision 7: Caching Strategy

**Decision**: TTL-based caching for pricing data (48h), event-based invalidation for user data

**Rationale**:
- **Pricing Data** (read-heavy, update-infrequent):
  - Cache in Redis with 48h TTL
  - Key: `pricing:{material_name}:{retailer}` → value: `{price, last_updated}`
  - Refresh: Background job every 48h (scraper)
  - Cache hit rate target: >80%

- **User Data** (read-write balanced):
  - No caching (or short 5-minute TTL)
  - User expects immediate updates after editing project
  - Event-based: Invalidate cache on project update (publish to Redis channel)

**Cache Warming**:
- Popular materials (top 100 by search volume) refreshed every 24h
- Long-tail materials refreshed on-demand (lazy load)

**Alternatives Considered**:
1. **Event-based invalidation for pricing**:
   - Pros: Always fresh data
   - Cons: Scraper doesn't run in real-time, 48h batch job
   - Rejected: TTL-based simpler and sufficient

2. **No caching** (always query DB):
   - Pros: Simpler, no stale data
   - Cons: Database load, slower response times
   - Rejected: Doesn't meet p95 <500ms latency without caching

**Implementation Notes**:
- Redis data structures:
  - Strings: `pricing:{key}` → JSON object
  - Sets: `popular_materials` → Set of material names
- Cache-aside pattern: Check cache → if miss, query DB → populate cache
- Monitoring: Track cache hit rate (target >80%), eviction rate

---

## Decision 8: Frontend State Management

**Decision**: React Query for server state, no global client state management (useState/Context sufficient)

**Rationale**:
- **Server State** (API data): React Query handles perfectly
  - Caching, background refetching, optimistic updates, devtools
  - Eliminates boilerplate for loading/error states
- **Client State** (UI state): Minimal needs
  - Form state: React Hook Form
  - Modal open/close: Local useState
  - Theme: Context API
- **No Redux/Zustand Needed**: EstiMate is not a complex SPA
  - No deeply nested state
  - No global state shared across many components
  - Server state dominates (projects, estimates, shopping lists)

**Alternatives Considered**:
1. **Zustand** (lightweight state management):
   - Pros: Simple, less boilerplate than Redux
   - Cons: Not needed for EstiMate's state complexity
   - Rejected: React Query + useState sufficient

2. **Redux Toolkit**:
   - Pros: Industry standard, powerful devtools
   - Cons: Overkill for this app, verbose
   - Rejected: Too complex for current needs

**Implementation Notes**:
- React Query configuration:
  - `staleTime`: 5 minutes (data considered fresh)
  - `cacheTime`: 30 minutes (cached data retained)
  - `refetchOnWindowFocus`: true (refresh on tab switch)
- Custom hooks wrapping React Query:
  - `useProjects()`, `useProject(id)`, `useShoppingList(id)`
- Optimistic updates: Mark item as purchased immediately, rollback on error

---

## Decision 9: Deployment Strategy

**Decision**: AWS ECS Fargate for backend, Vercel for frontend

**Rationale**:
- **Backend (ECS Fargate)**:
  - Containerized FastAPI app (Docker)
  - Serverless compute (no EC2 management)
  - Auto-scaling based on CPU/memory
  - Cost: ~$30-50/month at launch, scales to ~$200-300/month at 10K users
  - Simpler than EKS (no Kubernetes overhead)

- **Frontend (Vercel)**:
  - Optimized for React/Vite, instant deploys
  - Global CDN (edge caching)
  - Free tier: 100GB bandwidth/month (sufficient for launch)
  - Automatic HTTPS, preview deployments per PR
  - Cost: Free → $20/month (Pro) → $150/month (Team) as needed

**Alternatives Considered**:
1. **AWS EKS** (Kubernetes):
   - Pros: More control, advanced orchestration
   - Cons: $75/month cluster cost + complexity
   - Rejected: ECS sufficient for current scale

2. **AWS Lambda** (serverless):
   - Pros: Pay-per-request, ultra-scalable
   - Cons: Cold starts (500ms-2s), doesn't meet p95 <500ms latency
   - Rejected: Latency target not met

3. **Railway / Render** (simpler PaaS):
   - Pros: Very easy setup, good for MVP
   - Cons: Less control, higher cost at scale ($50/month → $500/month)
   - Reconsidered: Use Railway for MVP ($20/month), migrate to ECS if costs exceed $200/month

**Final Decision Revision**: **Use Railway for MVP**
- Faster setup (days vs weeks)
- PostgreSQL + Redis included
- $20/month for 1 service, $10/month per additional (DB, Redis)
- Migrate to ECS when traffic exceeds Railway's sweet spot (~50K users)

**Deployment Flow**:
- Git push to `main` → GitHub Actions → Deploy to Railway (backend) + Vercel (frontend)
- Staging environment: `develop` branch → Railway staging + Vercel preview
- Database migrations: Run Alembic migrations in GitHub Actions before deployment

---

## Decision 10: Monitoring & APM

**Decision**: Grafana Cloud (free tier) + Sentry for errors

**Rationale**:
- **Grafana Cloud**:
  - Free tier: 10K metrics, 50GB logs, 50GB traces/month
  - OpenTelemetry compatible (future-proof)
  - Prometheus metrics, Loki logs, Tempo traces (all in one)
  - Alerting included
  - Cost: Free → $49/month at scale

- **Sentry** (error tracking):
  - Free tier: 5K errors/month
  - Excellent Python & React SDKs
  - Source map support (unminified stack traces)
  - Performance monitoring included
  - Cost: Free → $26/month (Team)

**Alternatives Considered**:
1. **DataDog**:
   - Pros: Industry leading, everything in one platform
   - Cons: Expensive ($15/host/month minimum, $1K+/month at scale)
   - Rejected: Cost prohibitive for early stage

2. **New Relic**:
   - Pros: Good APM, generous free tier (100GB/month)
   - Cons: Less customizable dashboards than Grafana
   - Rejected: Grafana better for custom metrics

3. **Self-hosted Prometheus + Grafana**:
   - Pros: Free, full control
   - Cons: Maintenance burden, need to manage storage/retention
   - Rejected: Not core competency, managed service preferred

**Implementation Notes**:
- **Backend instrumentation**:
  - OpenTelemetry SDK (Python)
  - Metrics: Request count, latency, error rate, DB query time
  - Logs: Structured JSON (Python logging → Loki)
  - Traces: Every API request, DB query, external API call

- **Frontend instrumentation**:
  - Sentry React SDK
  - Performance monitoring: Page load time, API call latency
  - Error tracking: Unhandled exceptions, React errors

- **Dashboards**:
  - System health: API latency (p50, p95, p99), error rate, throughput
  - Business metrics: Signups, conversions (free → pro), active projects
  - Cost tracking: CV API calls, pricing scraper runs, storage usage

- **Alerts**:
  - P1 (page immediately): API error rate >5%, uptime <99%, auth down
  - P2 (alert in Slack): Latency p95 >1s, conversion rate drops >20%
  - P3 (email): Storage costs spike >$500/month

---

## Summary of Decisions

| Area | Decision | Cost (MVP) | Migration Trigger |
|------|----------|------------|-------------------|
| Computer Vision | Google Cloud Vision API | ~$10/month | >100K photos collected → custom model |
| Retailer APIs | Web scraping (Playwright) | ~$5/month (compute) | Official APIs available → migrate |
| Estimation | Rule-based algorithms | $0 | >10K feedback entries → ML model |
| Authentication | Supabase Auth | Free (<50K MAU) | >50K MAU → optimize costs |
| Database | PostgreSQL (Supabase/Railway) | Included | N/A |
| Photo Storage | Supabase Storage (MVP) | ~$20/month | >$500/month → migrate to S3 |
| Caching | Redis (Railway/Supabase) | Included | N/A |
| Frontend State | React Query | $0 | Complex state needs → add Zustand |
| Deployment | Railway + Vercel | ~$40/month | >50K users → AWS ECS/RDS |
| Monitoring | Grafana Cloud + Sentry | Free | >10K errors/month → paid tier |

**Total Estimated Monthly Cost (MVP)**: ~$100/month

**Total Estimated Monthly Cost (10K users)**: ~$500/month
- Railway: $200
- Supabase Storage: $100
- Cloud Vision: $50
- Vercel: $20
- Monitoring: $75
- Misc (DNS, email): $55

---

## Next Steps

1. ✅ All technology decisions finalized
2. → Proceed to Phase 1: Design & Contracts
   - Create `data-model.md` with PostgreSQL schema
   - Create `contracts/openapi.yaml` with API endpoints
   - Create `quickstart.md` with local setup instructions
   - Update agent context file with new technologies
