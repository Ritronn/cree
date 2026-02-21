# 🚀 Adaptive Learning System - Complete Integration Plan

## Overview
Integrating React frontend with Django backend + ML model for adaptive learning with monitoring, testing, and personalized difficulty adjustment.

---

## Phase 1: Backend - New Django Models ✅

### New App: `adaptive_learning`
```
learning/adaptive_learning/
├── models.py          # Topic, Content, Assessment, Question, UserProgress, etc.
├── views.py           # REST API endpoints
├── urls.py            # API routes
├── ml_predictor.py    # ML model integration
├── serializers.py     # DRF serializers
└── migrations/
```

### Models to Create:
1. **Topic** - User's learning topics
2. **Content** - YouTube/PDF/PPT/Word content
3. **Assessment** - Generated quizzes
4. **Question** - Individual questions
5. **UserAnswer** - Student responses with timestamps
6. **UserProgress** - Mastery levels, difficulty tracking
7. **MonitoringSession** - Tab switches, time tracking
8. **ConceptMastery** - Per-concept performance

---

## Phase 2: REST API Endpoints ✅

### Content Management
- `POST /api/topics/` - Create topic
- `GET /api/topics/` - List user's topics
- `GET /api/topics/{id}/` - Topic details
- `POST /api/content/` - Add content (YouTube/PDF/PPT/Word)
- `GET /api/content/{id}/` - Get content details

### Assessment & Testing
- `POST /api/assessments/generate/` - Auto-generate quiz from content
- `GET /api/assessments/{id}/` - Get assessment questions
- `POST /api/assessments/{id}/submit/` - Submit answer
- `GET /api/assessments/{id}/results/` - Get results with adaptive score

### Monitoring
- `POST /api/monitoring/track/` - Track tab switches, time
- `GET /api/monitoring/session/{id}/` - Get session stats

### Adaptive Learning
- `POST /api/adaptive/predict-difficulty/` - ML model prediction
- `GET /api/adaptive/next-questions/` - Get next set of questions
- `GET /api/progress/{topic_id}/` - Get mastery levels

---

## Phase 3: ML Model Integration ✅

### Files to Create:
```
learning/adaptive_learning/
├── ml_models/
│   ├── adaptive_model.pkl          # Trained model
│   ├── training_data.csv           # Synthetic data
│   └── model_performance.json      # Metrics
└── ml_predictor.py                 # Prediction logic
```

### ML Predictor Functions:
- `predict_next_difficulty(user_data)` - Returns 1, 2, or 3
- `calculate_adaptive_score(accuracy, time, attempts)` - Custom scoring
- `apply_business_rules(prediction, user_data)` - Enforce constraints

---

## Phase 4: Frontend Updates ✅

### New Components to Create:
```
frontend/src/
├── components/
│   ├── MonitoringOverlay.jsx      # Tab switch detection
│   ├── AssessmentWindow.jsx       # Quiz interface
│   ├── ResultsDashboard.jsx       # Stats & adaptive score
│   └── ProgressTracker.jsx        # Mastery visualization
├── services/
│   └── api.js                     # Axios API calls
└── utils/
    └── monitoring.js              # Tab switch tracking
```

### Update Existing Pages:
- **Dashboard.jsx** - Connect to backend API
- **TopicWindow.jsx** - Add monitoring, connect to content API
- **LearningWindow.jsx** - Integrate assessment API

---

## Phase 5: Monitoring & Testing Phase ✅

### Monitoring Features:
1. **Tab Switch Detection** - `document.visibilitychange` API
2. **Time Tracking** - Start/pause/resume timers
3. **Focus Tracking** - Detect when user leaves window
4. **Activity Logging** - Store all events in database

### Testing Features:
1. **Auto-generate Questions** - From YouTube transcripts/PDF text
2. **Immediate Feedback** - Show correct/incorrect with explanations
3. **Adaptive Scoring** - ML-based difficulty adjustment
4. **Concept Tracking** - Identify weak areas

---

## Phase 6: Integration Steps ✅

### Step 1: Create Django App
```bash
cd learning
python manage.py startapp adaptive_learning
```

### Step 2: Install Dependencies
```bash
# Backend
pip install djangorestframework django-cors-headers joblib scikit-learn youtube-transcript-api PyPDF2 python-docx python-pptx openai

# Frontend (already installed)
npm install axios
```

### Step 3: Update Django Settings
- Add `adaptive_learning` to `INSTALLED_APPS`
- Add `rest_framework` and `corsheaders`
- Configure CORS for React dev server

### Step 4: Create Models & Migrations
```bash
python manage.py makemigrations adaptive_learning
python manage.py migrate
```

### Step 5: Build REST API
- Create serializers
- Create views (APIView/ViewSets)
- Add URL routes

### Step 6: Integrate ML Model
- Load trained model
- Create prediction endpoint
- Test with sample data

### Step 7: Update React Frontend
- Create API service layer
- Connect components to backend
- Add monitoring logic

### Step 8: Test End-to-End
- Create topic → Add content → Take assessment → View results

---

## Tech Stack Summary

### Backend:
- Django 3.1.14
- Django REST Framework
- SQLite (migrate to Supabase later)
- scikit-learn (ML model)
- OpenAI API (question generation)
- youtube-transcript-api
- PyPDF2, python-docx, python-pptx

### Frontend:
- React 19.2.0
- Vite
- Tailwind CSS
- Framer Motion
- Axios
- react-pdf
- Lucide React (icons)

### ML:
- Random Forest Classifier
- 8 input features → 1 output (difficulty 1-3)
- Trained on 5k-10k synthetic samples

---

## Timeline (Hackathon Mode)

### Day 1: Backend Setup (6-8 hours)
- Create models
- Build REST API
- Integrate ML model

### Day 2: Frontend Integration (6-8 hours)
- Connect React to Django API
- Add monitoring features
- Build assessment interface

### Day 3: Testing & Polish (4-6 hours)
- End-to-end testing
- Bug fixes
- UI polish

---

## Next Steps

1. ✅ Create Django app structure
2. ✅ Define models
3. ✅ Build REST API
4. ✅ Integrate ML model
5. ✅ Update React frontend
6. ✅ Add monitoring features
7. ✅ Test everything
8. ✅ Deploy

---

**Let's start building! 🚀**
