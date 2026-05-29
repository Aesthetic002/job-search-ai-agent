# Job Search AI Agent

An AI-powered, microservices-based platform designed to automate and streamline the entire job search lifecycle. The system coordinates LangGraph-driven AI agents to analyze resumes, calculate ATS scores, recommend jobs, and administer mock interview rounds.

---

## 🚀 Key Features

*   **Premium Next.js Frontend:** A professional, light-mode, responsive dashboard with zero placeholders, interactive state management, and loading skeletons.
*   **Resume Parsing & ATS Scoring:** Upload resumes to Azure Cloud, extract details, and perform similarity alignment checks against job descriptions.
*   **Onboarding Gate:** Full-screen initial upload flow that automatically guides new users on their first visit.
*   **Kanban Application Board:** Fully interactive drag-and-drop manager tracking jobs across *Wishlist*, *Applied*, *Interviewing*, *Offer*, and *Rejected* stages.
*   **AI Mock Interview Simulator:** Configurable interview rounds with dynamic response evaluations.
*   **Horizontally Scalable Backend:** 5 FastAPI microservices coordinated via Docker Compose, Firestore, Redis, and Celery tasks.

---

## 🏛️ System Architecture

### Microservices Grid

| Service | Port | Description | Responsibility |
| :--- | :--- | :--- | :--- |
| **Auth Service** | `8001` | Handles user registration, JWT generation, bcrypt password hashing, and user profile databases. | Hemanth |
| **Jobs Service** | `8002` | Integrates external scrape clients (Indeed, Naukri) and processes listings. | Aaryan |
| **Resume Service** | `8003` | Coordinates file uploads to Azure Blob Storage, tracks Firestore records, and runs parsing. | Kaisen |
| **Interview Service** | `8004` | Orchestrates dynamic mock interviews and evaluations using the Interview Agent. | Kaisen |
| **Analytics Service** | `8005` | Computes dashboard analytics, application metrics, success rates, and weekly trend graphs. | Hemanth |

### Data Flow & Storage
*   **Primary Database:** **Firebase Firestore** stores users, resume metadata, applications, and job listings. Relational schemas are referenced using Firestore document IDs.
*   **Cloud File Storage:** **Azure Blob Storage** holds PDF and DOCX files securely within a unified `resumes/` container segment.
*   **Background Processing:** **Celery + Redis** handles long-running LangGraph agent cycles, email notifications, and parsing tasks asynchronously.

---

## 🔧 Installation & Setup

### Prerequisites
*   Node.js (v18+)
*   Python (3.9+)
*   Docker & Docker Compose
*   Firebase account service credentials (`firebase-credentials.json`)
*   Azure Connection Strings

### Step 1: Environment Variables
Copy `.env.example` to `.env` in the root folder:
```bash
cp .env.example .env
```
Fill in the credentials, including:
*   `DATABASE_URL` / Firestore setup parameters
*   `AZURE_CONNECTION_STRING`
*   `OPENAI_API_KEY` (for LangGraph agents)
*   `JWT_SECRET`

Place your service account JSON file in the root directory named as:
`firebase-credentials.json`

### Step 2: Launch the Infrastructure
Run Docker Compose to start Redis, Celery, and databases:
```bash
docker-compose up -d
```

### Step 3: Run the Backend Microservices
Launch the microservice servers using `uvicorn`. For example:
```bash
# Auth Service
python -m uvicorn backend.auth_service.main:app --port 8001

# Resume Service
python -m uvicorn backend.resume_service.main:app --port 8003
```

### Step 4: Start the Frontend Application
Navigate to the Next.js frontend directory, install dependencies, and run in development mode:
```bash
cd frontend/nextjs-app
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the portal.
