# API Contracts — Job Search AI Agent

> This document defines the API contracts between backend services and frontend.
> Frontend (Rohith) should build against these contracts.

---

## Auth Service (Port 8001) — Hemanth

### POST `/auth/register`
Register a new user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "minimum8chars",
  "full_name": "John Doe"
}
```

**Response (201):**
```json
{
  "user_id": 1,
  "message": "User registered successfully"
}
```

**Errors:**
- `400` — Email already registered

---

### POST `/auth/login`
Login and receive JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Errors:**
- `401` — Invalid email or password

---

### GET `/users/me`
Get current user profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2024-03-21T10:00:00Z"
}
```

**Errors:**
- `401` — Could not validate credentials

---

### PUT `/users/me`
Update current user profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "full_name": "John Updated",
  "email": "newemail@example.com"
}
```

**Response (200):**
```json
{
  "id": 1,
  "email": "newemail@example.com",
  "full_name": "John Updated",
  "created_at": "2024-03-21T10:00:00Z"
}
```

---

## Analytics Service (Port 8005) — Hemanth

### GET `/analytics/summary?user_id={id}`
Get complete analytics summary for a user.

**Query Parameters:**
- `user_id` (required): User ID to get analytics for

**Response (200):**
```json
{
  "total_applications": 25,
  "total_jobs_viewed": 150,
  "applications_by_status": {
    "applied": 15,
    "screening": 5,
    "interview": 3,
    "offer": 1,
    "rejected": 1
  },
  "weekly_applications": [
    {"date": "2024-03-15", "count": 3},
    {"date": "2024-03-16", "count": 5}
  ],
  "top_companies": [
    {"company": "Google", "application_count": 3},
    {"company": "Microsoft", "application_count": 2}
  ],
  "success_rate": 16.0
}
```

---

### GET `/analytics/applications?user_id={id}`
Get application statistics for a user.

**Query Parameters:**
- `user_id` (required): User ID

**Response (200):**
```json
{
  "total_applications": 25,
  "applications_by_status": {
    "applied": 15,
    "interview": 5,
    "offer": 2
  },
  "recent_applications": 8
}
```

---

### GET `/analytics/metrics/success-rate?user_id={id}`
Get success rate metric.

**Response (200):**
```json
{
  "metric_name": "success_rate",
  "value": 16.5,
  "description": "Percentage of applications resulting in interviews or offers"
}
```

---

### GET `/analytics/metrics/response-rate?user_id={id}`
Get response rate metric.

**Response (200):**
```json
{
  "metric_name": "response_rate",
  "value": 40.0,
  "description": "Percentage of applications that received a response"
}
```

---

### GET `/analytics/trends/weekly?user_id={id}&weeks={n}`
Get weekly application trends.

**Query Parameters:**
- `user_id` (required): User ID
- `weeks` (optional, default=4): Number of weeks (1-12)

**Response (200):**
```json
{
  "user_id": 1,
  "weeks": 4,
  "trends": [
    {"week": "2024-03-11", "applications": 5},
    {"week": "2024-03-18", "applications": 8}
  ]
}
```

---

## Common Response Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `201` | Created |
| `400` | Bad Request (validation error) |
| `401` | Unauthorized (missing/invalid token) |
| `404` | Not Found |
| `500` | Internal Server Error |

---

## Authentication Flow

1. User calls `POST /auth/register` to create account
2. User calls `POST /auth/login` to get JWT token
3. Include token in all subsequent requests:
   ```
   Authorization: Bearer <access_token>
   ```
4. Token expires after 24 hours — user must login again

---

## Notes for Frontend (Rohith)

- All requests to protected endpoints require `Authorization` header
- Store JWT token in secure storage (httpOnly cookie or secure localStorage)
- Handle 401 errors by redirecting to login
- Analytics endpoints require user_id as query parameter
- Use the health check endpoints (`/health`) to verify service availability

---

*Last updated: March 2026*
*Contributors: Hemanth (auth_service, analytics_service)*
