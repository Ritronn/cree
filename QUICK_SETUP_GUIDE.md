# Quick Setup Guide - Study Session Monitoring System

## 🚀 5-Minute Setup

### Step 1: Drop Your ML Model File
Place your `random_forest_classifier_model.joblib` file here:
```
learning/adaptive_learning/ml_models/random_forest_classifier_model.joblib
```

### Step 2: Configure Environment Variables
Create `learning/.env` file:
```bash
# Copy the example file
cp learning/.env.example learning/.env
```

Edit `learning/.env`:
```bash
# Get your Groq API key from: https://console.groq.com/
GROQ_API_KEY=gsk_your_actual_groq_api_key_here

# Replace with your RAG backend URL
RAG_BACKEND_URL=http://your-rag-backend-url/api/chat
```

### Step 3: Install Dependencies
```bash
pip install groq pytube hypothesis
```

### Step 4: Run the Server
```bash
cd learning
python manage.py runserver
```

### Step 5: Test It!
```bash
# Create a study session
curl -X POST http://localhost:8000/api/adaptive-learning/study-sessions/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your_token_here" \
  -d '{
    "content_id": 1,
    "session_type": "recommended"
  }'
```

---

## 📋 API Endpoints Cheat Sheet

### Session Management
```bash
# Create session
POST /api/adaptive-learning/study-sessions/
{
  "content_id": 1,
  "session_type": "recommended"  # or "standard"
}

# Get session status
GET /api/adaptive-learning/study-sessions/{id}/status/

# Start break
POST /api/adaptive-learning/study-sessions/{id}/start-break/

# End break
POST /api/adaptive-learning/study-sessions/{id}/end-break/

# Complete session
POST /api/adaptive-learning/study-sessions/{id}/complete/
{
  "difficulty": 1  # 1=Easy, 2=Medium, 3=Hard
}
```

### Monitoring
```bash
# Record event
POST /api/adaptive-learning/session-monitoring/
{
  "session_id": 1,
  "event_type": "video_pause",
  "event_data": {"timestamp": "2026-02-20T10:30:00Z"}
}

# Update metrics (call every 10 seconds)
POST /api/adaptive-learning/session-monitoring/update-metrics/
{
  "session_id": 1
}
```

### Proctoring
```bash
# Record violation
POST /api/adaptive-learning/proctoring/
{
  "session_id": 1,
  "event_type": "tab_switch"  # or "copy_attempt", "paste_attempt", etc.
}

# Get violations
GET /api/adaptive-learning/study-sessions/{id}/violations/
```

### Testing
```bash
# Generate test (automatic after session complete)
POST /api/adaptive-learning/tests/generate/
{
  "session_id": 1,
  "difficulty": 2
}

# Start test
POST /api/adaptive-learning/tests/{id}/start/

# Submit answer
POST /api/adaptive-learning/tests/{id}/submit-answer/
{
  "question_id": 1,
  "answer_text": "My answer",  # For short answer/problem solving
  "selected_index": 2,  # For MCQ (0-3)
  "time_taken_seconds": 45
}

# Complete test
POST /api/adaptive-learning/tests/{id}/complete/
```

### Whiteboard
```bash
# Capture screenshot
POST /api/adaptive-learning/whiteboard/
{
  "session_id": 1,
  "image_data": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "notes": "Optional notes"
}

# Download whiteboard
GET /api/adaptive-learning/whiteboard/download/?session_id=1
```

### Chat (RAG)
```bash
# Send query
POST /api/adaptive-learning/chat/
{
  "session_id": 1,
  "query": "What is the main concept in this video?",
  "context": "optional additional context"
}

# Get chat history
GET /api/adaptive-learning/chat/history/?session_id=1
```

---

## 🎯 Frontend Integration

### 1. Update API Service
Add to `frontend/src/services/api.js`:

```javascript
// Study Sessions
export const createStudySession = (contentId, sessionType) =>
  api.post('/adaptive-learning/study-sessions/', {
    content_id: contentId,
    session_type: sessionType
  });

export const getSessionStatus = (sessionId) =>
  api.get(`/adaptive-learning/study-sessions/${sessionId}/status/`);

export const startBreak = (sessionId) =>
  api.post(`/adaptive-learning/study-sessions/${sessionId}/start-break/`);

export const endBreak = (sessionId) =>
  api.post(`/adaptive-learning/study-sessions/${sessionId}/end-break/`);

export const completeSession = (sessionId, difficulty) =>
  api.post(`/adaptive-learning/study-sessions/${sessionId}/complete/`, {
    difficulty
  });

// Monitoring
export const recordMonitoringEvent = (sessionId, eventType, eventData) =>
  api.post('/adaptive-learning/session-monitoring/', {
    session_id: sessionId,
    event_type: eventType,
    event_data: eventData
  });

// Proctoring
export const recordProctoring = (sessionId, eventType) =>
  api.post('/adaptive-learning/proctoring/', {
    session_id: sessionId,
    event_type: eventType
  });

// Tests
export const generateTest = (sessionId, difficulty) =>
  api.post('/adaptive-learning/tests/generate/', {
    session_id: sessionId,
    difficulty
  });

export const submitAnswer = (testId, questionId, answerData) =>
  api.post(`/adaptive-learning/tests/${testId}/submit-answer/`, {
    question_id: questionId,
    ...answerData
  });

export const completeTest = (testId) =>
  api.post(`/adaptive-learning/tests/${testId}/complete/`);

// Whiteboard
export const captureWhiteboard = (sessionId, imageData, notes) =>
  api.post('/adaptive-learning/whiteboard/', {
    session_id: sessionId,
    image_data: imageData,
    notes
  });

// Chat
export const sendChatQuery = (sessionId, query, context) =>
  api.post('/adaptive-learning/chat/', {
    session_id: sessionId,
    query,
    context
  });
```

### 2. Update Monitoring
Add to `frontend/src/utils/monitoring.js`:

```javascript
// New event types
export const EVENT_TYPES = {
  ...existing_types,
  CAMERA_ENABLED: 'camera_enabled',
  CAMERA_DISABLED: 'camera_disabled',
  TAB_SWITCH: 'tab_switch',
  COPY_ATTEMPT: 'copy_attempt',
  PASTE_ATTEMPT: 'paste_attempt',
  SCREENSHOT_ATTEMPT: 'screenshot_attempt',
  WHITEBOARD_SNAPSHOT: 'whiteboard_snapshot',
  CHAT_QUERY: 'chat_query'
};
```

---

## 🔧 Troubleshooting

### Issue: Groq API not working
**Solution**: Check your API key in `.env` file. Get a free key from https://console.groq.com/

### Issue: YouTube playlist not extracting
**Solution**: Install pytube: `pip install pytube`

### Issue: RAG chat not responding
**Solution**: Update `RAG_BACKEND_URL` in `.env` with your actual RAG backend URL

### Issue: ML model not found
**Solution**: Place `random_forest_classifier_model.joblib` in `learning/adaptive_learning/ml_models/`

### Issue: Migrations not applied
**Solution**: Run `python manage.py migrate adaptive_learning`

---

## 📊 Testing the System

### 1. Create a Test Session
```python
# In Django shell
python manage.py shell

from adaptive_learning.models import User, Content, Topic
from adaptive_learning.session_manager import SessionManager

# Get or create test data
user = User.objects.first()
topic = Topic.objects.create(user=user, name="Test Topic")
content = Content.objects.create(
    topic=topic,
    title="Test Content",
    content_type="youtube",
    url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    transcript="Test transcript content",
    key_concepts=["concept1", "concept2"],
    processed=True
)

# Create session
session = SessionManager.create_session(user, content, 'recommended')
print(f"Session created: {session.id}")
```

### 2. Test Question Generation
```python
from adaptive_learning.question_generator import QuestionGenerator

qg = QuestionGenerator()
questions = qg.generate_mcq_questions(
    content.transcript,
    content.key_concepts,
    difficulty=1,
    count=5
)
print(f"Generated {len(questions)} questions")
```

### 3. Test RAG Chat
```python
from adaptive_learning.rag_chat_integration import RAGChatIntegration

result = RAGChatIntegration.send_query(
    session.id,
    "What is the main concept?",
    content.transcript
)
print(result)
```

---

## 🎉 You're All Set!

The backend is fully implemented and ready to use. Next steps:
1. Write property-based tests (40 properties)
2. Build frontend components
3. Deploy to staging

For detailed implementation info, see `IMPLEMENTATION_COMPLETE_SUMMARY.md`
