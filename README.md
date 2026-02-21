# 📝 Weekly Test Generator — N8N Automation (Groq AI)

Automated system that creates **weekly tests** from your study sessions using **n8n workflow automation** and **Groq AI**.

- ⏰ **Runs every Sunday at 10:00 AM** (IST)
- 📚 **Fetches all sessions** from the past 7 days for each user
- 🤖 **Generates tests using Groq AI** (Llama 3) with fallback
- ⏳ **Tests expire after 6 hours** automatically
- 📊 **Supports test submission** with auto-scoring

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    N8N WORKFLOW                          │
│                                                         │
│  ⏰ Schedule    →  📡 Fetch      →  🔄 Loop Each      │
│  (Sun 10AM)       Sessions          User               │
│                                                         │
│  🤖 AI Generate →  💾 Save Test  →  📧 Log/Notify     │
│  (Groq Llama 3)    (6hr Expiry)                        │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP
                         ▼
┌─────────────────────────────────────────────────────────┐
│              EXPRESS.JS API SERVER                       │
│                                                         │
│  GET  /api/users              List users                │
│  GET  /api/sessions?userId=X  User's weekly sessions    │
│  GET  /api/sessions/all-users All users' sessions       │
│  POST /api/tests              Create test (6hr expiry)  │
│  GET  /api/tests/:userId      Get active test           │
│  POST /api/tests/:id/submit   Submit & auto-score       │
│                                                         │
│  📦 SQLite Database (zero-config)                       │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your Groq API key:
GROQ_API_KEY=gsk_your_groq_key_here
GROQ_MODEL=llama3-70b-8192
```

### 3. Seed the Database

```bash
npm run seed
```

This creates the SQLite database with sample users and sessions.

### 4. Start the API Server

```bash
npm start
```

Server runs at **http://localhost:3000**

### 5. Import Workflow into n8n

1. Open your **n8n instance**
2. Go to **Workflows** → **Add Workflow** → **Import from File**
3. Select `weekly_test_workflow.json`
4. **Set environment variables** in n8n:
   - `API_BASE_URL` = `http://localhost:3000`
   - `GROQ_API_KEY` = your Groq API key
   - `GROQ_MODEL` = `llama3-70b-8192`
5. **Activate** the workflow

### 6. Test It Immediately (Manual Trigger)

Rather than waiting for Sunday, you can trigger the workflow now using the new manual webhook:

1. **In n8n**, ensure the workflow is active.
2. **Run this command** in your terminal:
   ```bash
   curl -X POST http://localhost:5678/webhook-test/trigger-weekly-test
   ```
   *Note: If using production webhook, remove `-test` from the URL.*

3. **Check the database**:
   ```bash
   # You can check if tests were created by viewing:
   GET http://localhost:3000/api/tests
   ```

### 🎮 Standalone Demo Prototype
For a full visual demonstration of the AI extraction and generation process, visit the **Demo Dashboard**:
👉 **[http://localhost:3000/demo.html](http://localhost:3000/demo.html)**

---

## ⏰ Schedule Details

| Setting | Value |
|---------|-------|
| **Trigger** | Every Sunday |
| **Time** | 10:00 AM IST |
| **Test Validity** | 6 hours (expires at 4:00 PM) |
| **Timezone** | Asia/Kolkata |

---

## 🔌 API Endpoints

### Health Check
```bash
GET /api/health
```

### List Users
```bash
GET /api/users
```

### Get User Sessions (Past 7 Days)
```bash
GET /api/sessions?userId=USER_ID&days=7
```

### Create Test
```bash
POST /api/tests
Content-Type: application/json

{
  "userId": "user-id",
  "title": "Weekly Test - Feb 21",
  "questions": [...],
  "totalQuestions": 15
}
```

---

## 🤖 AI Provider Setup

### Groq AI (Llama 3)
The workflow is configured to use **Groq** for lightning-fast test generation.
1. Get an API key from [console.groq.com](https://console.groq.com)
2. Add it to your `.env` and n8n environment variables.
3. The workflow uses `llama3-70b-8192` by default for high-quality educational content.

---

## 🎯 How It Works

1. **Sunday 10 AM** → n8n schedule trigger fires
2. **Fetches sessions** → calls `GET /api/sessions/all-users?days=7`
3. **For each user** → builds an AI prompt with all their session topics, key concepts, and summaries
4. **Groq generates test** → 10 MCQs + 5 short answers covering all weekly material
5. **Saves test** → `POST /api/tests` with 6-hour expiry timestamp
6. **Users access test** → `GET /api/tests/:userId` returns questions if not expired
