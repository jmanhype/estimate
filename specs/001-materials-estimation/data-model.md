# Data Model: EstiMate

**Feature**: EstiMate - AI Materials Estimation
**Date**: 2025-11-30
**Database**: PostgreSQL 15+
**ORM**: SQLAlchemy 2.0

---

## Entity Relationship Diagram

```
users (Supabase Auth)
  ↓ 1:N
projects
  ↓ 1:N
project_photos

projects
  ↓ 1:N
project_phases

projects
  ↓ 1:1
shopping_lists
  ↓ 1:N
shopping_list_items
  ↓ 1:N
retailer_prices (current, not historical)

projects
  ↓ 1:1
project_feedback (optional)

users
  ↓ 1:1
subscriptions
```

---

## Table Definitions

### `users` (Extended from Supabase Auth)

Managed by Supabase Auth, extended with application-specific fields.

**Supabase Auth Fields** (read-only via Supabase API):
- `id` (UUID, PK) - Supabase manages this
- `email` (TEXT) - From auth provider
- `created_at` (TIMESTAMPTZ) - Account creation
- `last_sign_in_at` (TIMESTAMPTZ) - Last login

**Application Extension Table** (`user_profiles`):

```sql
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  skill_level TEXT NOT NULL CHECK (skill_level IN ('beginner', 'intermediate', 'expert')),
  company_name TEXT, -- For Business tier users
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- RLS Policy
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only access their own profile"
  ON user_profiles FOR ALL
  USING (id = auth.uid());

-- Indexes
CREATE INDEX idx_user_profiles_skill_level ON user_profiles(skill_level);
```

**Rationale**: Separate table for app-specific fields keeps auth concerns separated. Supabase Auth handles authentication, we handle application metadata.

---

### `subscriptions`

Stores user subscription details synced from Stripe via webhooks.

```sql
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  stripe_subscription_id TEXT UNIQUE, -- Stripe subscription ID
  stripe_customer_id TEXT NOT NULL, -- Stripe customer ID
  tier TEXT NOT NULL CHECK (tier IN ('free', 'pro', 'business')),
  status TEXT NOT NULL CHECK (status IN ('active', 'canceled', 'past_due', 'trialing')),
  current_period_start TIMESTAMPTZ,
  current_period_end TIMESTAMPTZ,
  cancel_at_period_end BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  CONSTRAINT unique_user_subscription UNIQUE(user_id)
);

-- RLS Policy
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only access their own subscription"
  ON subscriptions FOR ALL
  USING (user_id = auth.uid());

-- Indexes
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_stripe_subscription_id ON subscriptions(stripe_subscription_id);
CREATE INDEX idx_subscriptions_tier ON subscriptions(tier);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
```

**Rationale**:
- Denormalized from Stripe for fast tier checks (avoid API calls)
- Updated via Stripe webhooks (`customer.subscription.*` events)
- `tier` determines feature access (enforced in API layer)

---

### `projects`

Represents a renovation project.

```sql
CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  project_type TEXT NOT NULL CHECK (project_type IN (
    'painting', 'flooring', 'tiling', 'drywall',
    'concrete', 'roofing', 'decking', 'fencing', 'kitchen', 'bathroom', 'other'
  )),
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'in_progress', 'completed')),
  budget_amount DECIMAL(10, 2), -- Optional budget in USD
  total_estimated_cost DECIMAL(10, 2), -- Calculated from shopping list
  total_actual_cost DECIMAL(10, 2), -- Sum of purchased items
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- RLS Policy
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only access their own projects"
  ON projects FOR ALL
  USING (user_id = auth.uid());

-- Indexes
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_created_at ON projects(created_at DESC);
CREATE INDEX idx_projects_user_created ON projects(user_id, created_at DESC); -- Dashboard query
```

**Validation Rules**:
- `name`: 1-200 characters
- `budget_amount`: Must be > 0 if provided
- Free tier users: Max 3 projects with status != 'completed'

---

### `project_photos`

Stores uploaded photos for computer vision analysis.

```sql
CREATE TABLE project_photos (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  storage_path TEXT NOT NULL, -- S3/Supabase Storage path
  file_size_bytes INTEGER NOT NULL,
  mime_type TEXT NOT NULL CHECK (mime_type IN ('image/jpeg', 'image/png', 'image/heic')),
  scan_status TEXT NOT NULL DEFAULT 'pending' CHECK (scan_status IN ('pending', 'clean', 'quarantined')),
  cv_analysis_status TEXT NOT NULL DEFAULT 'pending' CHECK (cv_analysis_status IN ('pending', 'processing', 'completed', 'failed')),
  cv_analysis_result JSONB, -- Stored CV API response
  cv_confidence_score DECIMAL(3, 2), -- 0.00-1.00
  uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- RLS Policy
ALTER TABLE project_photos ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only access photos from their projects"
  ON project_photos FOR ALL
  USING (
    project_id IN (
      SELECT id FROM projects WHERE user_id = auth.uid()
    )
  );

-- Indexes
CREATE INDEX idx_project_photos_project_id ON project_photos(project_id);
CREATE INDEX idx_project_photos_scan_status ON project_photos(scan_status);
CREATE INDEX idx_project_photos_cv_status ON project_photos(cv_analysis_status);
```

**cv_analysis_result Structure** (JSONB):
```json
{
  "room_dimensions": {
    "length_ft": 12.5,
    "width_ft": 10.0,
    "height_ft": 8.0
  },
  "features": {
    "doors": 1,
    "windows": 2,
    "irregular_shape": false
  },
  "confidence": 0.87,
  "api_provider": "google_cloud_vision",
  "raw_response": { ... }
}
```

**Constraints**:
- `file_size_bytes`: Max 10MB (10485760 bytes)
- Max 20 photos per project (enforced in API)

---

### `project_phases` (P3 feature, optional for MVP)

Represents timeline phases for multi-phase projects.

```sql
CREATE TABLE project_phases (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  phase_type TEXT NOT NULL CHECK (phase_type IN (
    'demo', 'framing', 'drywall', 'paint', 'flooring', 'tile', 'other'
  )),
  sequence_order INTEGER NOT NULL,
  estimated_start_date DATE,
  estimated_end_date DATE,
  estimated_duration_days INTEGER,
  actual_start_date DATE,
  actual_end_date DATE,
  status TEXT NOT NULL DEFAULT 'not_started' CHECK (status IN ('not_started', 'in_progress', 'completed')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  CONSTRAINT unique_project_sequence UNIQUE(project_id, sequence_order)
);

-- RLS Policy
ALTER TABLE project_phases ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only access phases from their projects"
  ON project_phases FOR ALL
  USING (
    project_id IN (
      SELECT id FROM projects WHERE user_id = auth.uid()
    )
  );

-- Indexes
CREATE INDEX idx_project_phases_project_id ON project_phases(project_id);
CREATE INDEX idx_project_phases_sequence ON project_phases(project_id, sequence_order);
```

---

### `shopping_lists`

One shopping list per project (1:1 relationship).

```sql
CREATE TABLE shopping_lists (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id UUID NOT NULL UNIQUE REFERENCES projects(id) ON DELETE CASCADE,
  total_estimated_cost DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- RLS Policy
ALTER TABLE shopping_lists ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only access shopping lists from their projects"
  ON shopping_lists FOR ALL
  USING (
    project_id IN (
      SELECT id FROM projects WHERE user_id = auth.uid()
    )
  );

-- Indexes
CREATE UNIQUE INDEX idx_shopping_lists_project_id ON shopping_lists(project_id);
```

**Rationale**: Separate table (vs embedding in projects) allows for future expansion (multiple quote scenarios).

---

### `shopping_list_items`

Individual material items in the shopping list.

```sql
CREATE TABLE shopping_list_items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  shopping_list_id UUID NOT NULL REFERENCES shopping_lists(id) ON DELETE CASCADE,
  material_name TEXT NOT NULL,
  material_category TEXT NOT NULL CHECK (material_category IN (
    'paint', 'primer', 'flooring', 'tile', 'grout', 'thinset',
    'lumber', 'concrete', 'roofing', 'decking', 'fasteners', 'other'
  )),
  calculated_quantity DECIMAL(10, 3) NOT NULL, -- Exact calculated amount
  waste_factor_percent DECIMAL(5, 2) NOT NULL, -- e.g., 15.00 for 15%
  actual_purchase_quantity DECIMAL(10, 3) NOT NULL, -- Rounded up to full units
  unit_of_measure TEXT NOT NULL CHECK (unit_of_measure IN (
    'gallons', 'square_feet', 'linear_feet', 'boxes', 'bags', 'pieces', 'each'
  )),
  estimated_unit_price DECIMAL(10, 2), -- Snapshot at estimation time
  estimated_total_cost DECIMAL(10, 2), -- = actual_purchase_quantity × estimated_unit_price
  actual_unit_price DECIMAL(10, 2), -- User-entered after purchase
  actual_total_cost DECIMAL(10, 2), -- = actual_purchase_quantity × actual_unit_price
  purchase_status TEXT NOT NULL DEFAULT 'not_purchased' CHECK (purchase_status IN ('not_purchased', 'purchased')),
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- RLS Policy
ALTER TABLE shopping_list_items ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only access items from their shopping lists"
  ON shopping_list_items FOR ALL
  USING (
    shopping_list_id IN (
      SELECT sl.id FROM shopping_lists sl
      JOIN projects p ON p.id = sl.project_id
      WHERE p.user_id = auth.uid()
    )
  );

-- Indexes
CREATE INDEX idx_shopping_list_items_list_id ON shopping_list_items(shopping_list_id);
CREATE INDEX idx_shopping_list_items_category ON shopping_list_items(material_category);
CREATE INDEX idx_shopping_list_items_purchase_status ON shopping_list_items(purchase_status);
```

**Calculation Example**:
```
Painting a 12' × 10' room with 8' ceilings, beginner skill level:

Wall Area = 2 × (12 + 10) × 8 - (2 doors × 20 sqft) - (2 windows × 15 sqft)
         = 352 - 40 - 30 = 282 sqft

Paint Needed = 282 sqft / 350 sqft per gallon = 0.806 gallons
Waste Factor = 10% (base) × 1.5 (beginner) = 15%
Adjusted = 0.806 × 1.15 = 0.927 gallons
Rounded Up = 1 gallon (sold in full gallons)

Record:
  calculated_quantity = 0.927
  waste_factor_percent = 15.00
  actual_purchase_quantity = 1.000
  unit_of_measure = 'gallons'
```

---

### `retailer_prices`

Current pricing data from retailers (not historical).

```sql
CREATE TABLE retailer_prices (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  material_name TEXT NOT NULL,
  material_category TEXT NOT NULL,
  retailer_name TEXT NOT NULL CHECK (retailer_name IN ('home_depot', 'lowes', 'menards', 'ace_hardware')),
  product_sku TEXT, -- Retailer's product SKU
  product_url TEXT,
  unit_price DECIMAL(10, 2) NOT NULL,
  unit_of_measure TEXT NOT NULL,
  availability_status TEXT NOT NULL DEFAULT 'unknown' CHECK (availability_status IN ('in_stock', 'out_of_stock', 'unknown')),
  last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  CONSTRAINT unique_material_retailer UNIQUE(material_name, retailer_name, unit_of_measure)
);

-- No RLS needed (public pricing data, no user_id)

-- Indexes
CREATE INDEX idx_retailer_prices_material ON retailer_prices(material_name);
CREATE INDEX idx_retailer_prices_category ON retailer_prices(material_category);
CREATE INDEX idx_retailer_prices_retailer ON retailer_prices(retailer_name);
CREATE INDEX idx_retailer_prices_last_updated ON retailer_prices(last_updated DESC);
CREATE INDEX idx_retailer_prices_lookup ON retailer_prices(material_name, retailer_name); -- Price lookup query
```

**Scraper Update Pattern**:
```sql
-- Upsert pricing data
INSERT INTO retailer_prices (material_name, material_category, retailer_name, unit_price, unit_of_measure, product_url, last_updated)
VALUES ('Interior Paint - Flat White', 'paint', 'home_depot', 24.98, 'gallons', 'https://...', NOW())
ON CONFLICT (material_name, retailer_name, unit_of_measure)
DO UPDATE SET
  unit_price = EXCLUDED.unit_price,
  product_url = EXCLUDED.product_url,
  availability_status = EXCLUDED.availability_status,
  last_updated = EXCLUDED.last_updated;
```

**Rationale**:
- No user_id (public pricing data)
- Denormalized (no join to materials table) for simplicity
- Updated by background scraper job every 48h

---

### `project_feedback` (P3 feature for AI learning)

Stores user feedback on estimation accuracy.

```sql
CREATE TABLE project_feedback (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id UUID NOT NULL UNIQUE REFERENCES projects(id) ON DELETE CASCADE,
  completion_status TEXT NOT NULL CHECK (completion_status IN ('completed', 'abandoned', 'partial')),
  accuracy_rating INTEGER CHECK (accuracy_rating BETWEEN 1 AND 5), -- 1=very inaccurate, 5=very accurate
  material_comparisons JSONB, -- Array of {material, estimated, actual, variance}
  user_notes TEXT,
  project_conditions JSONB, -- {uneven_walls: true, complex_cuts: true, ...}
  skill_level_at_completion TEXT,
  submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- RLS Policy
ALTER TABLE project_feedback ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only access feedback from their projects"
  ON project_feedback FOR ALL
  USING (
    project_id IN (
      SELECT id FROM projects WHERE user_id = auth.uid()
    )
  );

-- Indexes
CREATE INDEX idx_project_feedback_project_id ON project_feedback(project_id);
CREATE INDEX idx_project_feedback_submitted_at ON project_feedback(submitted_at DESC);
```

**material_comparisons Structure** (JSONB):
```json
[
  {
    "material": "Interior Paint - Flat White",
    "category": "paint",
    "estimated_quantity": 2.0,
    "actual_quantity_used": 1.8,
    "variance_percent": -10.0,
    "unit": "gallons"
  },
  {
    "material": "Painter's Tape",
    "category": "supplies",
    "estimated_quantity": 2,
    "actual_quantity_used": 3,
    "variance_percent": 50.0,
    "unit": "rolls"
  }
]
```

---

## Alembic Migration Plan

**Migration Sequence** (in order):

1. `001_create_user_profiles.py`:
   - Create `user_profiles` table
   - Enable RLS, create policies

2. `002_create_subscriptions.py`:
   - Create `subscriptions` table
   - Enable RLS, create policies
   - Seed default free tier for existing users

3. `003_create_projects.py`:
   - Create `projects` table
   - Enable RLS, create policies

4. `004_create_project_photos.py`:
   - Create `project_photos` table
   - Enable RLS, create policies

5. `005_create_shopping_lists.py`:
   - Create `shopping_lists` table
   - Enable RLS, create policies

6. `006_create_shopping_list_items.py`:
   - Create `shopping_list_items` table
   - Enable RLS, create policies

7. `007_create_retailer_prices.py`:
   - Create `retailer_prices` table
   - No RLS (public data)

8. `008_create_project_phases.py` (P3, optional for MVP):
   - Create `project_phases` table
   - Enable RLS, create policies

9. `009_create_project_feedback.py` (P3, optional for MVP):
   - Create `project_feedback` table
   - Enable RLS, create policies

**Rollback Strategy**:
- Each migration has `downgrade()` that drops tables in reverse dependency order
- Test rollback in staging before production deployment

---

## Database Performance Optimizations

### Connection Pooling

```python
# SQLAlchemy engine configuration
engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # Base connections
    max_overflow=90,       # Burst to 100 total
    pool_timeout=30,       # Wait 30s for connection
    pool_recycle=3600,     # Recycle connections after 1h
    pool_pre_ping=True,    # Check connection before use
)
```

### Query Optimizations

1. **Dashboard "Recent Projects" query**:
```sql
-- Uses idx_projects_user_created composite index
SELECT * FROM projects
WHERE user_id = ?
ORDER BY created_at DESC
LIMIT 10;
```

2. **Shopping List with Items query**:
```sql
-- Uses FK indexes, eager loading
SELECT sl.*, sli.*
FROM shopping_lists sl
JOIN shopping_list_items sli ON sli.shopping_list_id = sl.id
WHERE sl.project_id = ?;
```

3. **Price Comparison query**:
```sql
-- Uses idx_retailer_prices_lookup composite index
SELECT retailer_name, unit_price, product_url, last_updated
FROM retailer_prices
WHERE material_name = ?
ORDER BY unit_price ASC;
```

### Monitoring Queries

**Slow Query Detection**:
```sql
-- Enable pg_stat_statements extension
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Find slow queries (>100ms)
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC
LIMIT 20;
```

**Index Usage**:
```sql
-- Find unused indexes
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY schemaname, tablename;
```

---

## Data Retention & GDPR Compliance

### Retention Policies

**User Data**:
- Active accounts: Retained indefinitely while account active
- Deleted accounts: Hard delete after 30-day grace period
- Cascade deletes all associated projects, photos, shopping lists, feedback

**Pricing Data**:
- Current pricing: Retained indefinitely (or until material discontinued)
- Stale pricing (>90 days): Archive to cold storage

**Photos**:
- Active projects: Retained for duration of project
- Completed projects: Retained for 2 years, then deleted (cost optimization)
- Exception: User can request permanent deletion anytime

### GDPR Compliance

**Right to Access** (`/api/v1/users/me/export`):
```sql
-- Export all user data as JSON
SELECT json_build_object(
  'user', (SELECT row_to_json(up) FROM user_profiles up WHERE id = ?),
  'subscription', (SELECT row_to_json(s) FROM subscriptions s WHERE user_id = ?),
  'projects', (SELECT array_agg(row_to_json(p)) FROM projects p WHERE user_id = ?),
  'photos', (SELECT array_agg(row_to_json(pp)) FROM project_photos pp WHERE pp.project_id IN (SELECT id FROM projects WHERE user_id = ?)),
  'shopping_lists', (...)
);
```

**Right to Deletion** (`DELETE /api/v1/users/me`):
```sql
-- Cascade deletes via FK constraints
DELETE FROM user_profiles WHERE id = ?;
-- Cascades to: subscriptions, projects, project_photos, project_phases, shopping_lists, shopping_list_items, project_feedback

-- Also delete from Supabase Auth
-- (via Supabase Admin API)
```

---

## Testing Strategy

### Unit Tests (Repositories)

```python
# tests/unit/test_repositories/test_project_repository.py
def test_create_project(user_id):
    project = ProjectRepository.create(
        user_id=user_id,
        name="Test Project",
        project_type="painting"
    )
    assert project.id is not None
    assert project.status == "draft"

def test_tenant_isolation(user_a_id, user_b_id):
    project_a = ProjectRepository.create(user_id=user_a_id, ...)

    # User B should not be able to access User A's project
    with pytest.raises(PermissionError):
        ProjectRepository.get_by_id(project_a.id, user_id=user_b_id)
```

### Integration Tests (RLS Policies)

```python
# tests/integration/test_rls_policies.py
def test_rls_prevents_cross_user_access(db_session, user_a, user_b):
    # Create project as User A
    set_session_user(db_session, user_a.id)
    project = db_session.execute(
        insert(projects).values(user_id=user_a.id, name="A's Project").returning(projects.c.id)
    ).fetchone()

    # Try to access as User B
    set_session_user(db_session, user_b.id)
    result = db_session.execute(
        select(projects).where(projects.c.id == project.id)
    ).fetchone()

    assert result is None  # RLS policy blocked access
```

---

## Summary

**Total Tables**: 10 (8 for MVP, 2 for P3)

**MVP Tables**:
1. `user_profiles` - Extended user data
2. `subscriptions` - Stripe subscription sync
3. `projects` - Renovation projects
4. `project_photos` - Uploaded photos
5. `shopping_lists` - Material lists
6. `shopping_list_items` - Individual materials
7. `retailer_prices` - Pricing data
8. `project_phases` - Timeline (optional P3)

**Security**:
- ✅ Row-Level Security on all user tables
- ✅ Tenant isolation tested automatically
- ✅ GDPR compliance (export, delete)

**Performance**:
- ✅ Strategic indexes on FKs and query patterns
- ✅ Connection pooling (10-100 connections)
- ✅ Denormalized pricing for fast lookups

**Next**: Create OpenAPI contract based on this data model.
