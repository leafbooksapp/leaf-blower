# Leaf API Conventions

This document is the source of truth for API design decisions. All endpoints must follow these conventions — no exceptions without updating this doc first.

---

## Base URL

```
https://{api-id}.execute-api.us-west-2.amazonaws.com/prod/v1
```

---

## Versioning

- All endpoints are prefixed with `/v1/`
- When a breaking change is required, introduce `/v2/` alongside `/v1/` — never modify an existing versioned endpoint's contract
- Non-breaking additions (new optional fields, new endpoints) do not require a version bump
- Deprecate old versions with a `Deprecation` response header before removing them

---

## Authentication

All endpoints except `GET /v1/health` require a Cognito JWT.

```
Authorization: Bearer <id_token>
```

Requests without a valid token receive a `401` response. The handler extracts the user's UUID from the `sub` claim via `utils/auth.py`.

---

## Response Envelope

Every response — success or error — uses the same shape:

```json
{
  "data": { ... } | null,
  "error": { "code": "ERROR_CODE", "message": "Human readable description" } | null
}
```

**Success:**
```json
{
  "data": { "sub": "abc-123", "email": "user@example.com" },
  "error": null
}
```

**Error:**
```json
{
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Missing required query parameter: q"
  }
}
```

Use `utils/response.py` — never construct raw response dicts in handlers.

---

## Error Codes

| Code | HTTP Status | When to use |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Missing or invalid JWT |
| `FORBIDDEN` | 403 | Authenticated but not permitted to access this resource |
| `NOT_FOUND` | 404 | Resource does not exist |
| `VALIDATION_ERROR` | 400 | Invalid or missing request parameters |
| `CONFLICT` | 409 | Resource already exists (e.g. duplicate friend request) |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

## HTTP Methods

| Method | Usage |
|--------|-------|
| `GET` | Retrieve a resource or list — must be idempotent |
| `POST` | Create a resource, or trigger an action that doesn't map to CRUD |
| `PUT` | Replace a resource entirely |
| `PATCH` | Partial update |
| `DELETE` | Remove a resource |

---

## URL Naming

- Lowercase, hyphen-separated: `/friends/{id}/mutual-friends`
- Resource names are **plural nouns**: `/books`, `/friends`, `/shelves`
- IDs always in path, not query string: `/books/{id}` not `/books?id=`
- Actions that don't map cleanly to CRUD use `POST` with a verb noun: `POST /books/{id}/shelve`

---

## Pagination

All endpoints that return lists support cursor-based pagination.

**Request:**
```
GET /v1/books/search?q=dune&limit=20&cursor=eyJpZCI6IjEyMyJ9
```

**Response:**
```json
{
  "data": {
    "items": [ ... ],
    "next_cursor": "eyJpZCI6IjQ1NiJ9",
    "total": 84
  },
  "error": null
}
```

- `limit` defaults to 20, maximum 100
- `next_cursor` is `null` when there are no more pages
- Cursors are opaque — clients must not construct or parse them

---

## Project Structure

```
src/
  handlers/        # Lambda entry points — parse event, call domain, return envelope
  domain/          # Business logic — no AWS or HTTP concepts
  integrations/    # Aurora (RDS Data API) and external API calls
  models/          # Dataclasses (Book, Friend, etc.)
  utils/
    auth.py        # Cognito claim extraction
    response.py    # Envelope builder — use this, never raw dicts
    db.py          # RDS Data API client and param helper

infra/
  cloudformation/
    template.yaml  # All infrastructure — Lambdas, API Gateway, Aurora, Cognito

docs/
  api.md           # This file
```

---

## Adding a New Endpoint — Checklist

1. **Handler** — `src/handlers/{resource}.py`
   - Extract auth with `auth.get_user_id(event)` or `auth.get_claims(event)`
   - Return 401 immediately if unauthenticated
   - Parse and validate input; return `VALIDATION_ERROR` for bad input
   - Call into domain, return `response.success(...)` or `response.error(...)`

2. **Domain** — `src/domain/{concept}.py`
   - Pure business logic, no AWS SDK, no HTTP calls
   - One file per domain concept (e.g. `friends.py`, `shelves.py`)
   - If the concept is new, create a new file — don't add to an unrelated one

3. **Integrations** — `src/integrations/{concept}_db.py` or `{service}_api.py`
   - All RDS Data API calls live here
   - All external HTTP calls live here
   - No business logic — just data in / data out

4. **Model** — `src/models/{concept}.py` (if a typed shape is shared across layers)

5. **CloudFormation** — `infra/cloudformation/template.yaml`
   - New `AWS::Lambda::Function` with correct `Handler: handlers.{name}.lambda_handler`
   - New `AWS::ApiGateway::Resource` under `V1Resource`
   - New `AWS::ApiGateway::Method` with `AuthorizationType: COGNITO_USER_POOLS`
   - New `AWS::Lambda::Permission` for API Gateway

6. **GitHub Actions** — bump `DeploymentNonce` (handled automatically via `GITHUB_SHA`)

---

## Example: Adding `POST /v1/friends`

| Layer | File | Responsibility |
|-------|------|---------------|
| Handler | `src/handlers/friends.py` | Parse `friend_id` from body, call domain, return envelope |
| Domain | `src/domain/friends.py` | Check not already friends, check user exists, call persistence |
| Integration | `src/integrations/friends_db.py` | `add_friend()`, `get_friends()`, `is_friend()` SQL via RDS Data API |
| CloudFormation | `template.yaml` | `FriendsResource`, `FriendsPostMethod`, `FriendsFunction`, `FriendsLambdaPermission` |
