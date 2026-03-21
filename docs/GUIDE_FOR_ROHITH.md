# Contribution Guide for Rohith

## Frontend Dashboard Developer

**Branch:** `feature/frontend-dashboard`
**Phase:** 2 (Start after API contracts are published)
**Owner of:** `frontend/` folder

---

## 1. Overview

You are responsible for building the entire frontend of the Job Search AI Agent using Next.js. Your work depends on the backend APIs that Hemanth (auth, analytics) and Kaisen (resume, interview) are building.

**Your responsibilities:**
- Job search page with filters
- Kanban board for application tracking
- Resume upload UI
- Dark mode toggle
- Routing between pages
- REST API calls to backend services

---

## 2. Current Backend Status (What Hemanth Has Built)

### Database: Firestore + Azure Blob Storage

Hemanth has migrated the project from PostgreSQL to:
- **Firestore** - For user accounts, applications, analytics data
- **Azure Blob Storage** - For resume files (PDF, DOCX)

This means:
- User IDs are **strings** (not integers) - e.g., `"UauGnIb6pocvyVHQxar7"`
- All data is stored in the cloud (no local database needed)

### Working Endpoints (Port 8001)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/auth/register` | User registration |
| `POST` | `/auth/login` | Get JWT token |
| `GET` | `/users/me` | Get current user profile |
| `PUT` | `/users/me` | Update user profile |
| `DELETE` | `/users/me` | Delete account |
| `POST` | `/resumes/upload` | Upload resume file |
| `GET` | `/resumes/` | List user's resumes |
| `GET` | `/resumes/{id}` | Get resume details |
| `GET` | `/resumes/{id}/download` | Get download URL |
| `DELETE` | `/resumes/{id}` | Delete resume |

---

## 3. How to Set Up Your Development Environment

### Step 1: Clone and Create Your Branch

```bash
git clone <repo-url>
cd job-search-ai-agent
git checkout main
git pull origin main
git checkout -b feature/frontend-dashboard
```

### Step 2: Install Frontend Dependencies

```bash
cd frontend/nextjs-app
npm install
```

### Step 3: Create Environment File

Create `frontend/nextjs-app/.env.local`:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8001

# For development
NEXT_PUBLIC_ENV=development
```

### Step 4: Run Frontend

```bash
npm run dev
```

Frontend will be at: `http://localhost:3000`

---

## 4. API Integration Guide

### Authentication Flow

**1. User Registration**

```typescript
// lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function registerUser(email: string, password: string, fullName: string) {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, full_name: fullName })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Registration failed');
  }

  return response.json();
  // Returns: { id: "abc123", email: "user@example.com", full_name: "John Doe" }
}
```

**2. User Login**

```typescript
export async function loginUser(email: string, password: string) {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username: email, password })
  });

  if (!response.ok) {
    throw new Error('Invalid credentials');
  }

  const data = await response.json();
  // Returns: { access_token: "eyJ...", token_type: "bearer" }

  // Store token in localStorage or cookie
  localStorage.setItem('token', data.access_token);
  return data;
}
```

**3. Making Authenticated Requests**

```typescript
export async function getAuthHeaders() {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('Not authenticated');

  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
}

export async function getCurrentUser() {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/users/me`, { headers });

  if (!response.ok) {
    if (response.status === 401) {
      // Token expired - redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    throw new Error('Failed to get user');
  }

  return response.json();
  // Returns: { id: "abc123", email: "user@example.com", full_name: "John Doe" }
}
```

### Resume Upload

```typescript
export async function uploadResume(file: File) {
  const token = localStorage.getItem('token');

  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_URL}/resumes/upload`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
      // Don't set Content-Type - browser will set it with boundary
    },
    body: formData
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Upload failed');
  }

  return response.json();
  // Returns: { message: "Resume uploaded", resume_id: "xyz789", file_name: "resume.pdf" }
}
```

### List Resumes

```typescript
export async function getResumes() {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/resumes/`, { headers });

  return response.json();
  // Returns: { resumes: [{ id, file_name, file_size, uploaded_at, ... }] }
}
```

---

## 5. Files You Should Create

```
frontend/nextjs-app/
├── app/
│   ├── page.tsx              # Landing page
│   ├── layout.tsx            # Root layout with providers
│   ├── login/
│   │   └── page.tsx          # Login form
│   ├── register/
│   │   └── page.tsx          # Registration form
│   ├── dashboard/
│   │   └── page.tsx          # Main dashboard
│   ├── jobs/
│   │   └── page.tsx          # Job search page
│   ├── resume/
│   │   └── page.tsx          # Resume management
│   └── applications/
│       └── page.tsx          # Application tracking (Kanban)
├── components/
│   ├── Navbar.tsx            # Navigation bar
│   ├── JobCard.tsx           # Job listing card
│   ├── KanbanBoard.tsx       # Drag-drop application board
│   ├── ResumeUpload.tsx      # File upload component
│   ├── AuthProvider.tsx      # Auth context provider
│   └── ThemeProvider.tsx     # Dark mode provider
├── lib/
│   ├── api.ts                # API call helpers (use examples above)
│   └── auth.ts               # Auth utilities
├── hooks/
│   ├── useAuth.ts            # Auth hook
│   └── useResumes.ts         # Resume data hook
├── styles/
│   └── globals.css           # Tailwind + custom styles
├── types/
│   └── index.ts              # TypeScript types
├── package.json
└── tsconfig.json
```

---

## 6. TypeScript Types to Use

```typescript
// types/index.ts

export interface User {
  id: string;          // Firestore document ID (string, not number!)
  email: string;
  full_name: string;
  created_at?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: 'bearer';
}

export interface Resume {
  id: string;
  user_id: string;
  file_name: string;
  file_size: number;
  file_type: string;
  blob_url: string;
  parsed_text?: string;
  uploaded_at: string;
}

export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  description: string;
  salary_range?: string;
  posted_at: string;
}

export interface Application {
  id: string;
  user_id: string;
  job_id: string;
  company: string;
  status: 'applied' | 'screening' | 'interview' | 'offer' | 'rejected';
  applied_at: string;
}
```

---

## 7. Important Notes - Avoid Conflicts

### DO NOT Modify These Files

These files belong to Hemanth. Do not edit them:
- `backend/auth_service/*` - Auth backend (Hemanth)
- `backend/analytics_service/*` - Analytics backend (Hemanth)
- `config.py` - Firebase/Azure config (Hemanth)
- `backend/resume_file_service.py` - Resume upload logic (Hemanth)
- `backend/resume_routes.py` - Resume API routes (Hemanth)
- `agent/langgraph_workflows/*` - AI agents (Hemanth)

### Files You Can Modify

- Everything in `frontend/nextjs-app/`
- `requirements.txt` - Only to add frontend-related deps if needed

### Coordinate With

- **Kaisen** for resume parsing endpoints (`/resume/{id}/score`)
- **Aaryan** for job search endpoints (`/jobs/search`)

---

## 8. Testing Backend Locally

If you need to test with the backend:

### Option 1: Ask Hemanth for Test Credentials

Hemanth can provide Firebase and Azure credentials for a test environment.

### Option 2: Mock the API

Create mock responses for development:

```typescript
// lib/api.mock.ts
export const mockUser = {
  id: 'test123',
  email: 'test@example.com',
  full_name: 'Test User'
};

export const mockResumes = [
  { id: 'r1', file_name: 'resume.pdf', file_size: 245678, uploaded_at: '2024-03-21' }
];
```

---

## 9. Git Workflow

### Before Starting Work

```bash
git checkout feature/frontend-dashboard
git pull origin main  # Get latest from main
```

### Daily Commits

```bash
git add .
git commit -m "Add login page component"
git push origin feature/frontend-dashboard
```

### Merging (After Phase 2 Complete)

Coordinate with the team before merging to main. Make sure:
1. All API calls work with live backend
2. No conflicts with other branches
3. Code review completed

---

## 10. Questions?

- **API not working?** - Ask Hemanth
- **Resume parsing endpoints?** - Ask Kaisen
- **Job search endpoints?** - Ask Aaryan

---

**Start Date:** After `docs/API_CONTRACTS.md` is published
**Branch:** `feature/frontend-dashboard`
**Your Focus:** User interface only - no backend changes

Good luck!
