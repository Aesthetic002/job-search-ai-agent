# Credentials Setup Guide

Please provide the following credentials. I'll use these to configure the services.

---

## 1. Firebase Credentials

### Firebase Service Account JSON

1. Go to Firebase Console: https://console.firebase.google.com/
2. Select your project
3. Click gear icon → Project Settings
4. Go to "Service Accounts" tab
5. Click "Generate New Private Key"
6. Download the JSON file

**Action Required:**
- [ ] Save the downloaded JSON file as: `firebase-credentials.json`
- [ ] Place it in the project root: `d:\Skills\Projects\Capabl\job-search-ai-agent\firebase-credentials.json`

**OR** provide the JSON content below (I'll create the file):

```json
{
  "type": "service_account",
  "project_id": "YOUR_PROJECT_ID",
  "private_key_id": "...",
  "private_key": "...",
  "client_email": "...",
  "client_id": "...",
  "auth_uri": "...",
  "token_uri": "...",
  "auth_provider_x509_cert_url": "...",
  "client_x509_cert_url": "..."
}
```

### Firebase Project Details

```
Firebase Project ID: _________________
Firebase Storage Bucket: _________________ (usually: PROJECT_ID.appspot.com)
```

---

## 2. Azure Storage Credentials

### Azure Storage Connection String

1. Go to Azure Portal: https://portal.azure.com/
2. Navigate to your Storage Account
3. Go to "Access Keys" under Security + networking
4. Copy "Connection string" from key1 or key2

**Connection String Format:**
```
DefaultEndpointsProtocol=https;AccountName=YOUR_ACCOUNT_NAME;AccountKey=YOUR_KEY;EndpointSuffix=core.windows.net
```

### Azure Storage Details

```
Azure Storage Account Name: _________________
Azure Storage Connection String: _________________
Azure Container Name (for resumes): _________________ (e.g., "resumes")
```

---

## How to Provide These:

### Option 1 (Recommended - Secure):
Create the files directly:

1. **Firebase**: Save JSON as `firebase-credentials.json` in project root
2. **Azure**: I'll add to `.env` file (not committed to git)

### Option 2:
Paste them here in the chat, and I'll create the files for you.

---

## What I'll Do With These:

✅ Create `.env` file with Azure credentials
✅ Save Firebase credentials JSON
✅ Update `.gitignore` to exclude sensitive files
✅ Configure services to use Firestore + Azure Blob Storage
✅ Update all code to use the new setup

---

**Ready to provide credentials?**
Type "ready" when you have:
- Firebase JSON (file or content)
- Azure connection string
- Container name

Or ask me any questions!
