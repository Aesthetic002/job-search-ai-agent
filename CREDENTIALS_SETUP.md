# 🔑 Credentials & API Keys Setup Guide

This guide explains how to set up the credentials and API keys required to run the **Job Search AI Agent**. 

---

## ☁️ Why is Azure Storage Required?

The architecture uses a microservices structure where **Azure Blob Storage** acts as the primary cloud file storage system for the following reasons:
1. **Resume File Hosting**: Uploaded resume files (PDF, DOCX) must be stored in a centralized, secure location accessible by the **Resume Service** (handling upload) and the **Interview Service** (reading text content for questions).
2. **Decoupled Architecture**: Firestore (Firebase) is a database optimized for JSON documents and metadata, but not for storing binary file documents. Firestore only holds the metadata and references to the resumes, while the actual binary files are hosted on Azure Blob Storage.
3. **Fail-safe Uploads**: If Azure Blob Storage credentials are not set up or are incorrect, resume uploads will fail with connection errors, blocking resume parsing and ATS scoring workflows.

---

## 🛠️ Required Credentials Overview

Below is the list of all credentials, why they are required, and how to get them.

### 1. Firebase (Primary Database)
* **Used for**: Storing user profiles, resumes metadata, applications (Kanban status), and cached job listings.
* **Why it's required**: It is the centralized database of the entire application.
* **How to get it**:
  1. Go to the [Firebase Console](https://console.firebase.google.com/).
  2. Create a new project or select an existing one.
  3. Go to **Project Settings** (gear icon) -> **Service Accounts**.
  4. Click **Generate New Private Key** to download the service account credentials JSON file.
  5. Rename the downloaded file to `firebase-credentials.json` and place it in the root folder of this project.

---

### 2. Azure Storage Account
* **Used for**: Storing resume files (PDF/DOCX).
* **Why it's required**: To allow resume uploads and parsing to function without file upload failures.
* **How to get it**:
  1. Go to the [Azure Portal](https://portal.azure.com/).
  2. Create a new **Storage Account** (standard performance, hot tier).
  3. Navigate to the Storage Account -> under Security + Networking, click **Access keys**.
  4. Copy the **Connection string** (either key1 or key2).
  5. Go to **Data storage** -> **Containers**, and create a container named `resumes` (or custom name configured in `.env`).

---

### 3. LLM API Keys (Unified Fallback Chain)
We use a unified fallback LLM provider (`agent/llm_provider.py`) to guarantee the AI functionality runs entirely on **free-tier limits**. You should sign up for these keys to ensure complete fallback security:

#### A. Groq API Key (Primary LLM)
* **Used for**: Fast, high-quality resume parsing, ATS scoring, and interview question generation.
* **Why it's required**: Primary choice for agent operations.
* **How to get it**: Sign up at [Groq Console](https://console.groq.com/) and create an API Key (100% free limits).

#### B. Gemini API Key (Fallback)
* **Used for**: LLM fallback when Groq hits rate limits.
* **How to get it**: Sign up at [Google AI Studio](https://aistudio.google.com/) and generate an API Key (generous free tier).

#### C. OpenRouter API Key (Fallback)
* **Used for**: Calling free models (like `gemini-2.0-flash-exp:free` or `llama-3-8b:free`).
* **How to get it**: Create a free account at [OpenRouter](https://openrouter.ai/) and generate a key.

#### D. NVIDIA NIM API Key (Fallback)
* **Used for**: LLaMA-3.3-70B model execution fallback.
* **How to get it**: Sign up at [NVIDIA Build](https://build.nvidia.com/) to get 1,000 free credits.

#### E. Cohere API Key (Fallback)
* **Used for**: Last-mile fallback (Command-R model).
* **How to get it**: Sign up at [Cohere Dashboard](https://dashboard.cohere.com/) for a free developer key.

---

### 4. JWT Secret & Security
* **Used for**: Signing and verifying JSON Web Tokens (JWT) for secure user authentication in the Next.js frontend.
* **How to get it**: Any random, strong cryptographic string can be used. For example, run:
  ```powershell
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
  Set this value as `JWT_SECRET` in your `.env`.

---

### 5. Redis URL
* **Used for**: Broker database for Celery asynchronous background tasks and cache store.
* **How to get it**: Set it to `redis://localhost:6379/0` (standard local Redis). For production, you can use [Redis Cloud](https://redis.com/try-free/) or any hosted Redis provider.

---

## 📝 Configuration Steps

1. Create a `.env` file in the root of the project by copying `.env.example`:
   ```powershell
   cp .env.example .env
   ```
2. Fill in the keys:
   ```env
   # Firebase Settings
   FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
   FIREBASE_PROJECT_ID=your-project-id
   FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com

   # Azure Settings
   AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=YOUR_NAME;AccountKey=YOUR_KEY;EndpointSuffix=core.windows.net
   AZURE_STORAGE_ACCOUNT_NAME=your-storage-account-name
   AZURE_STORAGE_CONTAINER=resumes

   # Redis
   REDIS_URL=redis://localhost:6379/0

   # LLM Keys
   GROQ_API_KEY=gsk_...
   GEMINI_API_KEY=AIzaSy...
   OPENROUTER_API_KEY=sk-or-v1-...
   NVIDIA_API_KEY=nvapi-...
   COHERE_API_KEY=...

   # Authentication
   JWT_SECRET=your-generated-random-hex-string
   ```
3. Place your Firebase private key JSON file in the project root folder as `firebase-credentials.json`.
4. Ensure `.env` and `firebase-credentials.json` are **never committed to Git** (already configured in `.gitignore`).
