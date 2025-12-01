# EstiMate API Contracts

**Version**: 1.0.0
**Base URL**: `https://api.estimate.app/api/v1`
**Documentation**: OpenAPI 3.1 schema in `openapi.yaml`

---

## Overview

The EstiMate API provides RESTful endpoints for AI-powered materials estimation for home renovations. All endpoints require authentication via Supabase Auth JWT tokens, except health checks.

---

## Authentication

### Bearer Token (JWT)

All API requests (except `/health`) must include a valid Supabase Auth JWT token in the `Authorization` header:

```http
Authorization: Bearer <your_jwt_token>
```

**Obtaining a Token**:
1. Frontend: Use Supabase JS client to authenticate user (email/password, OAuth, magic link)
2. Supabase returns JWT containing `user_id`, `email`, `role`
3. Include token in all API requests

**Token Expiration**:
- Access tokens expire after 1 hour
- Use refresh tokens to obtain new access tokens without re-authentication
- Supabase client handles refresh automatically

**Example** (Python with httpx):
```python
import httpx

headers = {
    "Authorization": f"Bearer {jwt_token}",
    "Content-Type": "application/json"
}

response = httpx.get(
    "https://api.estimate.app/api/v1/projects",
    headers=headers
)
```

**Example** (JavaScript with Axios):
```javascript
const response = await axios.get('/api/v1/projects', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

---

## Rate Limiting

To ensure fair usage and service stability, API requests are rate-limited:

| User Type | Limit | Window |
|-----------|-------|--------|
| Unauthenticated | 10 requests | per minute |
| Authenticated (Free) | 100 requests | per minute |
| Authenticated (Pro/Business) | 100 requests | per minute |

**Rate Limit Headers** (included in all responses):
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1638360000
```

**429 Response** (Rate Limit Exceeded):
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests, try again in 45 seconds"
  }
}
```

**Best Practices**:
- Cache responses where appropriate (pricing data, project lists)
- Use pagination for list endpoints (`limit` and `offset` parameters)
- Implement exponential backoff for retries on 429 errors

---

## Versioning

API versions are specified in the URL path:

```
https://api.estimate.app/api/v1/projects
                             ^^^ version
```

**Version Policy**:
- **Major version** (`v1`, `v2`): Breaking changes
  - Field removals, type changes, endpoint removals
  - Announced 6 months in advance
  - Previous major version supported for 12 months

- **Minor/Patch versions**: Backward-compatible changes
  - New optional fields, new endpoints
  - No URL change (still `/api/v1/...`)
  - Tracked in OpenAPI schema version (`1.2.0`, `1.2.1`)

**Deprecation**:
- Deprecated fields marked in OpenAPI with `deprecated: true`
- Sunset date included in response headers: `Sunset: Sat, 01 Jan 2026 00:00:00 GMT`
- Migration guide published at https://docs.estimate.app/migrations

---

## Error Handling

All errors return consistent JSON structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "additional context (optional)"
    }
  }
}
```

### Common Error Codes

| HTTP Status | Code | Description |
|-------------|------|-------------|
| 400 | `INVALID_REQUEST` | Malformed request, validation failed |
| 400 | `VALIDATION_ERROR` | Request body validation failed |
| 401 | `UNAUTHORIZED` | Missing or invalid authentication token |
| 403 | `FORBIDDEN` | Authenticated but insufficient permissions |
| 403 | `PROJECT_LIMIT_REACHED` | Free tier limit (3 projects) exceeded |
| 403 | `PHOTO_LIMIT_REACHED` | Photo limit (20 per project) exceeded |
| 404 | `NOT_FOUND` | Resource not found (project, photo, etc.) |
| 409 | `CONFLICT` | Resource already exists |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests, retry after delay |
| 500 | `INTERNAL_ERROR` | Server error, contact support |
| 503 | `SERVICE_UNAVAILABLE` | Temporary outage, retry with backoff |

### Validation Errors

Validation errors include field-specific details:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "name": "Project name must be between 1 and 200 characters",
      "budget_amount": "Must be a positive number"
    }
  }
}
```

---

## Pagination

List endpoints support pagination via `limit` and `offset` query parameters:

```http
GET /api/v1/projects?limit=20&offset=40
```

**Parameters**:
- `limit`: Number of items to return (default: 10, max: 100)
- `offset`: Number of items to skip (default: 0)

**Response**:
```json
{
  "data": [...],
  "total": 150,
  "limit": 20,
  "offset": 40
}
```

**Calculating Pages**:
```
Page 1: offset=0, limit=20
Page 2: offset=20, limit=20
Page 3: offset=40, limit=20
...
Total Pages = ceil(total / limit)
```

---

## Filtering & Sorting

Some endpoints support filtering via query parameters:

**Projects Filtering**:
```http
GET /api/v1/projects?status=in_progress&limit=10
```

Supported filters:
- `status`: Filter by project status (`draft`, `in_progress`, `completed`)

**Sorting**:
- Default: `created_at DESC` (newest first)
- Custom sorting not yet supported (planned for v1.1)

---

## Async Operations

Some operations are asynchronous (photo CV analysis):

**Request** (POST `/projects/{id}/photos/{photoId}/analyze`):
```json
POST /api/v1/projects/abc-123/photos/xyz-789/analyze
```

**Response** (202 Accepted):
```json
{
  "photo_id": "xyz-789",
  "status": "processing",
  "message": "Analysis in progress, check status via GET /photos/{photoId}"
}
```

**Polling** (GET `/projects/{id}/photos/{photoId}`):
```javascript
async function waitForAnalysis(projectId, photoId) {
  while (true) {
    const photo = await getPhoto(projectId, photoId);

    if (photo.cv_analysis_status === 'completed') {
      return photo.cv_analysis_result;
    } else if (photo.cv_analysis_status === 'failed') {
      throw new Error('CV analysis failed');
    }

    // Wait 2 seconds before polling again
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
}
```

**Alternative: WebSockets** (planned for v1.2):
- Real-time updates for long-running operations
- Subscribe to `projects/{id}/photos/{photoId}/analysis` channel

---

## Idempotency

**POST** and **PATCH** operations are idempotent where possible:

**Creating Projects**:
- Duplicate project names allowed (no uniqueness constraint)
- Multiple requests create multiple projects

**Updating Items**:
- **PATCH** operations are idempotent
- Sending same update multiple times produces same result

**Retrying Failed Requests**:
- Safe to retry GET, PUT, PATCH, DELETE
- Retry POST only if you receive no response (network error)
- If POST returns 201, do not retry (resource already created)

---

## CORS (Cross-Origin Resource Sharing)

API allows CORS for frontend applications:

**Allowed Origins**:
- `https://estimate.app` (production)
- `https://staging.estimate.app` (staging)
- `http://localhost:3000` (local development)

**Allowed Methods**: `GET`, `POST`, `PATCH`, `DELETE`, `OPTIONS`

**Allowed Headers**: `Authorization`, `Content-Type`, `X-Requested-With`

**Credentials**: Supported (`Access-Control-Allow-Credentials: true`)

---

## Webhooks (Stripe Integration)

Stripe sends webhooks for subscription events:

**Endpoint**: `POST /api/v1/webhooks/stripe`

**Events Handled**:
- `customer.subscription.created` - New subscription
- `customer.subscription.updated` - Subscription changed (upgrade/downgrade)
- `customer.subscription.deleted` - Subscription canceled
- `invoice.payment_succeeded` - Payment successful
- `invoice.payment_failed` - Payment failed

**Webhook Verification**:
- Stripe signature verified using `Stripe-Signature` header
- Invalid signatures rejected with 400 error

**Automatic Actions**:
- Update `subscriptions` table with new tier/status
- Send email notifications for payment failures
- Enforce tier limits (project count, features)

---

## Data Formats

### Dates & Times

All timestamps are in **ISO 8601 format with UTC timezone**:

```json
{
  "created_at": "2025-11-30T15:30:00.000Z"
}
```

**Parsing** (JavaScript):
```javascript
const date = new Date("2025-11-30T15:30:00.000Z");
```

**Parsing** (Python):
```python
from datetime import datetime
date = datetime.fromisoformat("2025-11-30T15:30:00.000Z".replace("Z", "+00:00"))
```

### Decimals

Monetary amounts and measurements use **decimal strings** (not floats):

```json
{
  "budget_amount": "1500.00",
  "calculated_quantity": "2.750"
}
```

**Rationale**: Avoid floating-point precision errors in financial calculations.

**Parsing** (JavaScript):
```javascript
const amount = parseFloat("1500.00"); // Use for display only
const precise = new Decimal("1500.00"); // Use decimal.js for calculations
```

**Parsing** (Python):
```python
from decimal import Decimal
amount = Decimal("1500.00")
```

### Enums

Enum values are **lowercase with underscores**:

```json
{
  "project_type": "living_room_repaint",
  "status": "in_progress"
}
```

**Validation**: Invalid enum values return 400 error with allowed values in `details`.

---

## Testing

### Sandbox Environment

**Staging API**: `https://staging-api.estimate.app/api/v1`

- Separate database from production
- Safe for testing integrations
- Data reset weekly
- Free tier limits enforced

**Test Accounts**:
- Create via Supabase Auth staging instance
- No real payment methods required
- Stripe test mode enabled

### OpenAPI Validation

Validate requests/responses against OpenAPI schema:

**Tools**:
- [Swagger Editor](https://editor.swagger.io/) - Visual editor, validation
- [Prism](https://stoplight.io/open-source/prism) - Mock server
- [Spectral](https://stoplight.io/open-source/spectral) - Linting

**Example** (validate with Prism):
```bash
# Mock API server from OpenAPI spec
prism mock openapi.yaml

# Test against mock
curl http://localhost:4010/api/v1/projects
```

---

## SDK / Client Libraries

**Official SDKs** (planned for v1.1):
- Python: `estimate-python` (PyPI)
- JavaScript/TypeScript: `@estimate/client` (npm)
- Go: `github.com/estimate/go-client`

**Until then, use HTTP clients**:
- Python: `httpx`, `requests`
- JavaScript: `axios`, `fetch`
- Go: `net/http`

**Example Client Wrapper** (TypeScript):
```typescript
class EstimateClient {
  constructor(private token: string) {}

  async getProjects() {
    const response = await fetch('/api/v1/projects', {
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    });
    return response.json();
  }

  async createProject(data: CreateProjectRequest) {
    const response = await fetch('/api/v1/projects', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    return response.json();
  }
}
```

---

## Support

**Documentation**: https://docs.estimate.app/api
**Status Page**: https://status.estimate.app
**Support Email**: api@estimate.app
**GitHub Issues**: https://github.com/estimate/api-issues

**SLA**:
- **Uptime**: 99.5% (excluding planned maintenance)
- **Response Time**: p95 < 500ms for GET requests
- **Incident Response**: <2 hours for P1 incidents

---

## Changelog

### v1.0.0 (2025-11-30)

Initial release:
- Authentication via Supabase Auth
- Project CRUD operations
- Photo upload with presigned S3 URLs
- CV analysis (async)
- Material estimation generation
- Shopping list management
- Price comparison (P2)
- Subscription management (Stripe)
- Rate limiting (100 req/min)
- Error handling & validation
- Pagination support
