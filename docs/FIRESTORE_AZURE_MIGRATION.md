# Firestore + Azure Migration - Complete Summary

## 🎯 What Was Changed

Your project has been completely refactored to use:
- **Firestore** (instead of PostgreSQL) for all user data and analytics
- **Azure Blob Storage** (instead of local storage) for resume files and media

---

## ✅ Completed Tasks

### 1. **Dependencies Updated** (`requirements.txt`)
   - ✅ Added `firebase-admin==6.4.0` for Firestore
   - ✅ Added `azure-storage-blob==12.19.0` for Azure Blob Storage
   - ✅ Added `PyPDF2`, `python-docx`, `pdf2image`, `Pillow` for file parsing
   - ✅ Commented out PostgreSQL dependencies (SQLAlchemy, psycopg2)

### 2. **Configuration Module** (`config.py`)
   - ✅ Firebase initialization and Firestore client setup
   - ✅ Azure Blob Storage client setup
   - ✅ Helper functions for file upload/download/delete
   - ✅ Signed URL generation for secure downloads

### 3. **Auth Service Refactored**
   Files changed:
   - ✅ `backend/auth_service/dependencies.py` - Now uses Firestore
   - ✅ `backend/auth_service/schemas.py` - Updated IDs to strings
   - ✅ `backend/auth_service/routes/auth.py` - Firestore queries
   - ✅ `backend/auth_service/routes/users.py` - Firestore queries

### 4. **Analytics Service Refactored**
   Files changed:
   - ✅ `backend/analytics_service/dependencies.py` - Now uses Firestore
   - ✅ `backend/analytics_service/routes/analytics.py` - Firestore queries

### 5. **Resume File Service Created**
   New files:
   - ✅ `backend/resume_file_service.py` - Azure Blob Storage integration
   - ✅ `backend/resume_routes.py` - Resume upload/download API endpoints

### 6. **Environment & Security**
   - ✅ `.env.example` updated with Firebase and Azure variables
   - ✅ `.gitignore` updated to exclude `firebase-credentials.json`
   - ✅ `CREDENTIALS_SETUP.md` created with instructions

---

## 📋 What You Need to Do

### Step 1: Provide Credentials

You need to provide these credentials:

#### Firebase Credentials:
1. Go to Firebase Console → Project Settings → Service Accounts
2. Click "Generate New Private Key"
3. Save the JSON file as: **`firebase-credentials.json`**
4. Place it in the project root: `d:\Skills\Projects\Capabl\job-search-ai-agent\`

#### Azure Storage Credentials:
1. Go to Azure Portal → Storage Account → Access Keys
2. Copy the **Connection String**
3. Add it to your `.env` file

### Step 2: Update `.env` File

Create or update `d:\Skills\Projects\Capabl\job-search-ai-agent\.env`:

```env
# Firebase (Firestore Database)
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com

# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=YOUR_ACCOUNT;AccountKey=YOUR_KEY;EndpointSuffix=core.windows.net
AZURE_STORAGE_ACCOUNT_NAME=your-storage-account-name
AZURE_STORAGE_ACCOUNT_KEY=your-storage-account-key
AZURE_STORAGE_CONTAINER=resumes

# Redis (for Celery broker and cache)
REDIS_URL=redis://localhost:6379/0

# OpenAI API Key (for LangGraph agents)
OPENAI_API_KEY=your-openai-api-key

# External Job APIs
NAUKRI_API_KEY=your-naukri-api-key
INDEED_API_KEY=your-indeed-api-key

# JWT Authentication
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000

# Service Ports
AUTH_SERVICE_PORT=8001
JOBS_SERVICE_PORT=8002
RESUME_SERVICE_PORT=8003
INTERVIEW_SERVICE_PORT=8004
ANALYTICS_SERVICE_PORT=8005
```

### Step 3: Install New Dependencies

```bash
cd d:/Skills/Projects/Capabl/job-search-ai-agent
pip install -r requirements.txt
```

### Step 4: Test Configuration

```bash
python config.py
```

**Expected Output:**
```
==================================================
Testing Configuration
==================================================

Testing Firebase...
✅ Firestore connection successful

Testing Azure Blob Storage...
✅ Azure Blob Storage connection successful
   Container: resumes

==================================================
```

---

## 🗄️ New Database Structure

### Firestore Collections:

#### 1. **users** Collection
```
users/
  {user_id}/
    - email: string
    - hashed_password: string
    - full_name: string
    - created_at: timestamp
    - updated_at: timestamp
```

#### 2. **resumes** Collection
```
resumes/
  {resume_id}/
    - user_id: string
    - file_name: string
    - file_path: string (Azure blob path)
    - file_size: number
    - file_type: string (.pdf, .docx)
    - blob_url: string
    - parsed_text: string (extracted text)
    - uploaded_at: timestamp
    - updated_at: timestamp
```

#### 3. **applications** Collection
```
applications/
  {application_id}/
    - user_id: string
    - job_id: string
    - company: string
    - status: string (applied, screening, interview, offer, rejected)
    - applied_at: timestamp
    - updated_at: timestamp
```

#### 4. **jobs** Collection
```
jobs/
  {job_id}/
    - title: string
    - company: string
    - location: string
    - description: string
    - created_at: timestamp
```

###Azure Blob Storage Structure:

```
resumes/ (container)
  ├── {user_id}/
  │   ├── {resume_id}.pdf
  │   ├── {resume_id}.docx
  │   └── ...
  └── ...
```

---

## 🚀 New API Endpoints

### Resume Management Endpoints:

```
POST   /resumes/upload           - Upload resume file (PDF, DOCX, TXT)
GET    /resumes/                 - List all user's resumes
GET    /resumes/{resume_id}      - Get resume metadata + parsed text
GET    /resumes/{resume_id}/download  - Get temporary download URL
DELETE /resumes/{resume_id}      - Delete resume
PUT    /resumes/{resume_id}/reparse   - Re-parse resume file
```

### Example Usage:

**Upload Resume:**
```bash
curl -X POST http://localhost:8001/resumes/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@resume.pdf"
```

**Response:**
```json
{
  "message": "Resume uploaded successfully",
  "resume_id": "abc123",
  "file_name": "resume.pdf",
  "file_size": 245678,
  "parsed_text_length": 3500
}
```

---

## 🔄 What Changed in Existing APIs

### Auth Service (Port 8001)
- ✅ User IDs are now **strings** (not integers)
- ✅ All operations use Firestore (no PostgreSQL needed)
- ✅ API contracts remain the same

### Analytics Service (Port 8005)
- ✅ User IDs are now **strings** in query parameters
- ✅ All operations use Firestore
- ✅ API contracts remain the same

### Example:
```bash
# Before (PostgreSQL):
GET /analytics/summary?user_id=1

# After (Firestore):
GET /analytics/summary?user_id=abc123xyz
```

---

## 🧪 Testing the New Setup

### 1. Start Redis (for Celery)
```bash
docker run -d -p 6379:6379 redis:7
```

### 2. Start Auth Service
```bash
cd d:/Skills/Projects/Capabl/job-search-ai-agent
python -m uvicorn backend.auth_service.main:app --port 8001 --reload
```

### 3. Start Analytics Service
```bash
python -m uvicorn backend.analytics_service.main:app --port 8005 --reload
```

### 4. Test User Registration
```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'
```

### 5. Test Resume Upload (with token)
```bash
curl -X POST http://localhost:8001/resumes/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@your-resume.pdf"
```

---

## 📦 What's No Longer Needed

### Can Be Removed:
- ❌ Docker PostgreSQL container
- ❌ `docker-compose.yml` postgres service
- ❌ SQLAlchemy models (but kept for reference)

### Can Keep (for reference):
- backend/auth_service/models.py (legacy)
- backend/analytics_service/models.py (legacy)

---

## 🆘 Troubleshooting

### Error: `firebase-credentials.json not found`
**Solution:** Place your Firebase service account JSON in the project root.

### Error: `AZURE_STORAGE_CONNECTION_STRING not found`
**Solution:** Add Azure connection string to `.env` file.

### Error: `Could not import config module`
**Solution:** Make sure `config.py` is in the project root directory.

### Error: Resume upload fails
**Solution:** Check Azure container exists and credentials are correct.

---

## 📊 Cost Estimates

### Firestore (Free Tier):
- ✅ 50,000 reads/day
- ✅ 20,000 writes/day
- ✅ 20,000 deletes/day
- ✅ 1GB storage

### Azure Blob Storage:
- ~$0.02/GB/month for storage
- ~$0.005/10,000 operations

### Estimated Monthly Cost (100 users):
- Firestore: **FREE** (within limits)
- Azure Storage: **< $5/month**

---

## 🎉 Benefits of This Migration

### Firestore Advantages:
- ✅ No server management
- ✅ Real-time sync
- ✅ Automatic scaling
- ✅ Free tier sufficient for MVP
- ✅ Cloud-based (accessible anywhere)

### Azure Blob Storage Advantages:
- ✅ Reliable file storage
- ✅ CDN integration
- ✅ Secure signed URLs
- ✅ Automatic backups
- ✅ Low cost

---

## ⏭️ Next Steps

1. **Provide credentials** (see Step 1-2 above)
2. **Install dependencies** (`pip install -r requirements.txt`)
3. **Test configuration** (`python config.py`)
4. **Test services** (follow testing guide)
5. **Commit changes** (when ready)

---

**Migration Status:** ✅ Code Complete - Waiting for Credentials

**Author:** Hemanth
**Date:** March 21, 2026
**Branch:** `feature/langgraph-agent`
