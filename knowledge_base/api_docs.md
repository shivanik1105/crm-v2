# API Documentation

## Rate Limits

All API endpoints are subject to rate limiting based on subscription tier:

### Starter Tier
- **Limit:** 100 requests per minute
- **Burst:** 150 requests
- **Scope:** Per API key

### Standard Tier
- **Limit:** 500 requests per minute
- **Burst:** 750 requests
- **Scope:** Per API key
- **Webhooks:** Available (up to 10 endpoints)

### Enterprise Tier
- **Limit:** Unlimited requests
- **Burst:** No cap
- **Scope:** Per organization
- **Webhooks:** Unlimited endpoints
- **Dedicated API gateway available**

## API Versions

### v1 API (Deprecated)
- **Status:** Deprecated as of 2024-01-01
- **Sunset Date:** 2024-07-01
- **Authentication:** Bearer token in `Authorization` header
- **Response format:** Flat JSON
- **Action Required:** Migrate to v2 before sunset date

### v2 API (Current)
- **Status:** Active and recommended
- **Authentication:** New auth header `X-API-Key-V2`
- **Response envelope:** All responses wrapped in `{"data": ..., "meta": {...}}`
- **Breaking changes:**
  - All endpoints now under `/v2/` prefix
  - Pagination uses cursor-based instead of offset
  - Error responses include `error_code` field
  - Webhook payloads include `version: "v2"` field

## Webhooks

### Supported Events
- `contact.created`
- `contact.updated`
- `email.received`
- `thread.updated`
- `escalation.created`

### Configuration
Webhook endpoints can be configured in the Developer Dashboard. Only Standard+ tiers can create webhooks.

### Retry Policy
- 3 retries with exponential backoff (1s, 5s, 25s)
- Webhooks disabled after 10 consecutive failures
- Reactivation requires manual confirmation in dashboard

## Authentication

### API Keys
Generate API keys from Settings > Developer. Keys are scoped to the organization.

### IP Whitelisting
Enterprise customers can configure IP whitelisting for additional security.

## Common Endpoints

### POST /v2/contacts
Create a new contact. Requires `email`, `name`, and `tier` fields.

### GET /v2/contacts/{id}
Retrieve contact by ID. Returns full contact profile with metadata.

### GET /v2/threads
List threads with pagination. Supports filtering by status, category, and date range.
