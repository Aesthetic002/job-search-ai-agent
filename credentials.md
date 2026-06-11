# 🔐 External Credentials Setup Guide

Your application code is functionally complete! However, before you can deploy to production, you need to set up a few external cloud services. 

This document explains **what** accounts you need, **why** you need them, and **where** to put the credentials.

---

## 1. Azure Blob Storage (Required for Resumes)
**Why it's required:** Currently, uploaded resumes are saved to a temporary local folder (`/tmp` or similar). When you deploy your backend to a cloud host (like Render or AWS), the local filesystem is ephemeral—meaning any uploaded resume will be deleted as soon as the server restarts. Azure Blob Storage provides permanent, secure cloud storage for these files.
**How to get it:**
1. Go to the [Azure Portal](https://portal.azure.com/).
2. Create a **Storage Account**.
3. Create a **Container** named `resumes` (make sure it is set to Private).
4. Go to **Access keys** and copy the Connection String.
**Where to put it:**
Add this to your `.env` file (and your production host's environment variables):
```env
AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=YOUR_ACCOUNT_NAME;AccountKey=YOUR_ACCOUNT_KEY;EndpointSuffix=core.windows.net"
```

## 2. Firebase / Firestore (Required for Database)
**Why it's required:** Right now, the application gracefully degrades to in-memory/stub data if Firebase isn't connected. To actually save user profiles, cached job scrapes, and interview histories persistently across sessions, you need Firestore.
**How to get it:**
1. Go to the [Firebase Console](https://console.firebase.google.com/).
2. Create a new project and enable **Firestore Database**.
3. Go to **Project Settings > Service Accounts**.
4. Click **Generate new private key**. It will download a JSON file.
**Where to put it:**
Save the JSON file in your project root as `firebase-adminsdk.json` (ensure this is in `.gitignore` so it isn't pushed to GitHub!).
Add this to your `.env`:
```env
FIREBASE_CREDENTIALS_PATH="firebase-adminsdk.json"
```

## 3. LLM API Keys (Required for AI Features)
**Why it's required:** Your application uses a highly resilient 5-provider fallback chain (Groq, OpenRouter, NVIDIA, Gemini, Cohere) for things like mock interviews, resume parsing, and salary benchmarking.
**Where to put it:**
Ensure these are filled out in your `.env` file. You already have some of these set up locally, but you must ensure they are copied over to your production deployment environment variables.
```env
GROQ_API_KEY="..."
OPENROUTER_API_KEY="..."
NVIDIA_API_KEY="..."
GEMINI_API_KEY="..."
COHERE_API_KEY="..."
```

## 4. SendGrid (Optional — For Email Alerts)
**Why it's required:** If you want the Celery background workers to send actual weekly job alert emails to users.
**How to get it:**
1. Sign up at [SendGrid](https://sendgrid.com/).
2. Generate an API Key under Settings > API Keys.
**Where to put it:**
```env
SENDGRID_API_KEY="SG.your_api_key_here"
```

---

## 🚀 Deployment Next Steps
Once you have these credentials:
1. Choose a hosting provider (e.g., Render for Backend, Vercel for Frontend).
2. Paste the contents of your `.env` file into the host's Environment Variables settings.
3. Update `.github/workflows/cd.yml` with your host's deployment token to enable continuous deployment.
