# Testing Guide - Hemanth's Implementation

Complete guide to test all features: Auth Service, Analytics Service, LangGraph Workflows, and Celery Tasks.

---

## 📋 Prerequisites

- ✅ Docker Desktop installed and running
- ✅ Python 3.11+ installed
- ✅ Git bash or WSL (for running bash scripts on Windows)
- ✅ curl (comes with Git bash)

---

## 🚀 Quick Start (Recommended)

### Option 1: Run Everything with Docker Compose

1. **Start all services:**
   ```bash
   cd d:/Skills/Projects/Capabl/job-search-ai-agent
   docker-compose up -d postgres redis
   ```

2. **Wait 10 seconds for database to initialize:**
   ```bash
   sleep 10
   ```

3. **Run services locally (simpler for testing):**
   ```bash
   # Terminal 1 - Auth Service
   cd d:/Skills/Projects/Capabl/job-search-ai-agent
   pip install -r requirements.txt
   python -m uvicorn backend.auth_service.main:app --host 0.0.0.0 --port 8001

   # Terminal 2 - Analytics Service
   cd d:/Skills/Projects/Capabl/job-search-ai-agent
   python -m uvicorn backend.analytics_service.main:app --host 0.0.0.0 --port 8005
   ```

4. **Run automated tests:**
   ```bash
   bash test_services.sh
   ```

---

## 🧪 Manual Testing (Step-by-Step)

### Step 1: Start Infrastructure

```bash
cd d:/Skills/Projects/Capabl/job-search-ai-agent

# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Check if running
docker ps
```

**Expected Output:**
```
CONTAINER ID   IMAGE          PORTS                    STATUS
abc123...      postgres:15    0.0.0.0:5432->5432/tcp   Up
def456...      redis:7        0.0.0.0:6379->6379/tcp   Up
```

---

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected:** All packages install successfully (may take 2-3 minutes)

---

### Step 3: Start Auth Service

```bash
# Open a new terminal
cd d:/Skills/Projects/Capabl/job-search-ai-agent
python -m uvicorn backend.auth_service.main:app --host 0.0.0.0 --port 8001 --reload
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001
```

**Test it:**
```bash
curl http://localhost:8001/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "auth_service",
  "version": "1.0.0"
}
```

---

### Step 4: Start Analytics Service

```bash
# Open another new terminal
cd d:/Skills/Projects/Capabl/job-search-ai-agent
python -m uvicorn backend.analytics_service.main:app --host 0.0.0.0 --port 8005 --reload
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8005
```

**Test it:**
```bash
curl http://localhost:8005/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "analytics_service",
  "version": "1.0.0"
}
```

---

### Step 5: Test Auth Endpoints

#### 5.1 Register a New User

```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "hemanth@example.com",
    "password": "password123",
    "full_name": "Hemanth Test"
  }'
```

**Expected Response:**
```json
{
  "user_id": 1,
  "message": "User registered successfully"
}
```

#### 5.2 Login (Get JWT Token)

```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "hemanth@example.com",
    "password": "password123"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**💡 Copy the access_token for next steps!**

#### 5.3 Get Current User Profile

```bash
# Replace YOUR_TOKEN with the actual token from login
curl -X GET http://localhost:8001/users/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response:**
```json
{
  "id": 1,
  "email": "hemanth@example.com",
  "full_name": "Hemanth Test",
  "created_at": "2026-03-21T08:30:00"
}
```

#### 5.4 Update User Profile

```bash
curl -X PUT http://localhost:8001/users/me \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Hemanth Updated"
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "email": "hemanth@example.com",
  "full_name": "Hemanth Updated",
  "created_at": "2026-03-21T08:30:00"
}
```

---

### Step 6: Test Analytics Endpoints

#### 6.1 Get Analytics Summary

```bash
curl http://localhost:8005/analytics/summary?user_id=1
```

**Expected Response:**
```json
{
  "total_applications": 0,
  "total_jobs_viewed": 0,
  "applications_by_status": {
    "applied": 0,
    "screening": 0,
    "interview": 0,
    "offer": 0,
    "rejected": 0
  },
  "weekly_applications": [],
  "top_companies": [],
  "success_rate": 0.0
}
```

#### 6.2 Get Application Statistics

```bash
curl http://localhost:8005/analytics/applications?user_id=1
```

**Expected Response:**
```json
{
  "total_applications": 0,
  "applications_by_status": {},
  "recent_applications": 0
}
```

#### 6.3 Get Success Rate

```bash
curl http://localhost:8005/analytics/metrics/success-rate?user_id=1
```

**Expected Response:**
```json
{
  "metric_name": "success_rate",
  "value": 0.0,
  "description": "Percentage of applications resulting in interviews or offers"
}
```

#### 6.4 Get Weekly Trends

```bash
curl http://localhost:8005/analytics/trends/weekly?user_id=1&weeks=4
```

**Expected Response:**
```json
{
  "user_id": 1,
  "weeks": 4,
  "trends": []
}
```

---

### Step 7: Test with API Client (Postman/Insomnia)

#### Import this collection:

**Auth Service Endpoints:**
```
POST   http://localhost:8001/auth/register
POST   http://localhost:8001/auth/login
GET    http://localhost:8001/users/me         (requires token)
PUT    http://localhost:8001/users/me         (requires token)
DELETE http://localhost:8001/users/me         (requires token)
GET    http://localhost:8001/health
GET    http://localhost:8001/docs             (Swagger UI)
```

**Analytics Service Endpoints:**
```
GET http://localhost:8005/analytics/summary?user_id=1
GET http://localhost:8005/analytics/applications?user_id=1
GET http://localhost:8005/analytics/metrics/success-rate?user_id=1
GET http://localhost:8005/analytics/metrics/response-rate?user_id=1
GET http://localhost:8005/analytics/trends/weekly?user_id=1&weeks=4
GET http://localhost:8005/health
GET http://localhost:8005/docs                              (Swagger UI)
```

---

### Step 8: Test LangGraph Workflows (Python)

Create a test file: `test_langgraph.py`

```python
from agent.langgraph_workflows import create_job_search_workflow

# Create workflow
workflow = create_job_search_workflow()

# Initial state
initial_state = {
    "user_id": "user123",
    "user_profile": {
        "desired_role": "Python Developer",
        "skills": ["Python", "FastAPI", "PostgreSQL"],
        "experience_level": "Mid-level",
        "location": "Remote"
    },
    "resume": {
        "full_name": "Hemanth Test",
        "email": "hemanth@example.com",
        "summary": "Experienced Python developer",
        "skills": ["Python", "FastAPI"]
    },
    "next_stage": "job_search"
}

# Run workflow
print("Running LangGraph workflow...")
result = workflow.invoke(initial_state)
print(f"Workflow completed with status: {result.get('status')}")
```

Run it:
```bash
python test_langgraph.py
```

---

### Step 9: Test Celery Tasks

#### 9.1 Start Celery Worker

```bash
# New terminal
cd d:/Skills/Projects/Capabl/job-search-ai-agent
celery -A celery_worker worker --loglevel=info
```

**Expected Output:**
```
 -------------- celery@DESKTOP v5.3.6
---- **** -----
--- * ***  * -- Windows-10.0.26200
-- * - **** ---
- ** ---------- [config]
- ** ---------- .> app:         job_search_agent:0x...
- ** ---------- .> transport:   redis://localhost:6379/0
- ** ---------- .> results:     redis://localhost:6379/0
*** --- * --- .> concurrency:  4 (prefork)
-- **** ---
--- ***** ---- [queues]
 -------------- .> default          exchange=default(direct)
```

#### 9.2 Test Task Execution (Python)

```python
from celery_worker import search_jobs_task, health_check

# Test health check
result = health_check.delay()
print(result.get(timeout=10))

# Test job search
result = search_jobs_task.delay(
    user_id="user123",
    search_criteria={
        "title": "Python Developer",
        "skills": ["Python", "FastAPI"],
        "location": "Remote"
    }
)
print(result.get(timeout=30))
```

---

## 🌐 Interactive API Documentation

Both services provide interactive Swagger UI:

- **Auth Service:** http://localhost:8001/docs
- **Analytics Service:** http://localhost:8005/docs

You can test all endpoints directly in the browser!

---

## 🐛 Troubleshooting

### Issue 1: Port Already in Use

```bash
# Windows - Kill process on port
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

### Issue 2: Database Connection Failed

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Issue 3: Redis Connection Failed

```bash
# Check if Redis is running
docker ps | grep redis

# Restart Redis
docker-compose restart redis
```

### Issue 4: Import Errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Issue 5: JWT Token Invalid

- Token expires after 24 hours
- Login again to get a new token
- Check JWT_SECRET in .env matches the service

---

## ✅ Testing Checklist

- [ ] PostgreSQL running (port 5432)
- [ ] Redis running (port 6379)
- [ ] Auth service running (port 8001)
- [ ] Analytics service running (port 8005)
- [ ] User registration works
- [ ] User login returns JWT token
- [ ] JWT authentication works
- [ ] User profile CRUD works
- [ ] Analytics summary endpoint works
- [ ] Analytics metrics endpoints work
- [ ] LangGraph workflow runs
- [ ] Celery worker connects
- [ ] Celery tasks execute
- [ ] Swagger UI accessible

---

## 📊 Expected Test Results

When you run `bash test_services.sh`, you should see:

```
================================
🧪 Testing Job Search AI Agent
================================

[1/10] Testing Auth Service Health...
✅ PASS - Auth service is running

[2/10] Testing Analytics Service Health...
✅ PASS - Analytics service is running

[3/10] Testing User Registration...
✅ PASS - User registered successfully (ID: 1)

[4/10] Testing User Login...
✅ PASS - Login successful (Token received)

[5/10] Testing Get Current User Profile...
✅ PASS - User profile retrieved successfully

[6/10] Testing Update User Profile...
✅ PASS - User profile updated successfully

[7/10] Testing Analytics Summary...
✅ PASS - Analytics summary retrieved successfully

[8/10] Testing Analytics Applications...
✅ PASS - Application statistics retrieved successfully

[9/10] Testing Analytics Success Rate...
✅ PASS - Success rate metric retrieved successfully

[10/10] Testing Analytics Weekly Trends...
✅ PASS - Weekly trends retrieved successfully

================================
✅ All Tests Completed!
================================
```

---

## 🎯 Next Steps After Testing

1. **If all tests pass:**
   - Document any issues found
   - Share results with team
   - Ready for integration testing

2. **If tests fail:**
   - Check error messages
   - Verify environment variables
   - Check service logs
   - Review troubleshooting section

3. **Performance testing:**
   - Use Apache Bench or k6 for load testing
   - Test concurrent users
   - Monitor database performance

---

## 📞 Need Help?

- Check service logs for errors
- Review API documentation at `/docs`
- Check `.env` file configuration
- Verify Docker containers are running

---

*Last Updated: March 21, 2026*
*Author: Hemanth*
