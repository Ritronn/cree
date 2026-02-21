# Adaptive Learning System - Setup Instructions

## Quick Start Guide

### Prerequisites
- Python 3.8+
- Node.js 16+
- pip and npm installed

### Backend Setup

1. **Navigate to the learning directory**
```bash
cd learning
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
pip install -r adaptive_learning_requirements.txt
```

3. **Train the ML model**
```bash
python adaptive_learning/train_model.py
```

4. **Run database migrations**
```bash
python manage.py makemigrations adaptive_learning
python manage.py migrate
```

5. **Create a superuser (optional)**
```bash
python manage.py createsuperuser
```

6. **Start the Django development server**
```bash
python manage.py runserver
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to the frontend directory**
```bash
cd frontend
```

2. **Install Node dependencies**
```bash
npm install
```

3. **Start the Vite development server**
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## API Endpoints

### Topics
- `GET /api/adaptive/topics/` - List all topics
- `POST /api/adaptive/topics/` - Create new topic
- `GET /api/adaptive/topics/{id}/` - Get topic details
- `GET /api/adaptive/topics/{id}/progress/` - Get topic progress
- `GET /api/adaptive/topics/{id}/concepts/` - Get concept mastery

### Content
- `POST /api/adaptive/content/upload/` - Upload content (YouTube/PDF/PPT/Word)
- `GET /api/adaptive/content/{id}/` - Get content details
- `POST /api/adaptive/content/{id}/generate_assessment/` - Generate quiz

### Assessments
- `GET /api/adaptive/assessments/{id}/` - Get assessment
- `GET /api/adaptive/assessments/{id}/questions/` - Get questions
- `POST /api/adaptive/assessments/{id}/submit_answer/` - Submit answer
- `POST /api/adaptive/assessments/{id}/complete/` - Complete and get results

### Monitoring
- `POST /api/adaptive/monitoring/start_session/` - Start monitoring
- `POST /api/adaptive/monitoring/{id}/track_event/` - Track event
- `POST /api/adaptive/monitoring/{id}/end_session/` - End session

### Progress
- `GET /api/adaptive/progress/` - List all progress
- `GET /api/adaptive/progress/overview/` - Get overview

## User Workflow

1. **Create a Topic**
   - User creates a topic (e.g., "Python Programming")

2. **Add Content**
   - Upload YouTube video, PDF, PPT, or Word document
   - System extracts content and identifies key concepts

3. **Generate Assessment**
   - System generates 10 questions based on content
   - Questions adapt to user's current difficulty level

4. **Take Assessment**
   - User answers questions in the learning window
   - System tracks time, tab switches, and engagement

5. **View Results**
   - See score, adaptive score, and weak concepts
   - ML model predicts next difficulty level

6. **Continue Learning**
   - Add more content or retake assessments
   - System adapts difficulty based on performance

## Configuration

### Django Settings
- CORS is configured for `localhost:5173` and `localhost:3000`
- Session authentication is enabled
- File uploads are stored in `media/learning_content/`

### Environment Variables (Optional)
- `OPENAI_API_KEY` - For AI-powered question generation (falls back to templates if not set)

## Troubleshooting

### CORS Errors
- Ensure Django server is running on port 8000
- Check that CORS_ALLOWED_ORIGINS includes your frontend URL

### File Upload Issues
- Ensure `media/` directory exists and is writable
- Check file size limits in Django settings

### ML Model Not Found
- Run `python adaptive_learning/train_model.py` to generate the model
- Ensure `ml_models/adaptive_model.pkl` exists

### Database Errors
- Delete `db.sqlite3` and run migrations again
- Check that all migrations are applied

## Features

### Monitoring Phase
- Tab switch detection
- Focus tracking
- Time spent tracking
- Engagement metrics

### Testing Phase
- Auto-generated quizzes from content
- Multiple difficulty levels (1-3)
- Immediate feedback
- Performance statistics

### Adaptive Learning Phase
- ML-based difficulty prediction
- Concept mastery tracking
- Spaced repetition for weak concepts
- Personalized learning paths

## Next Steps

1. Test the complete workflow end-to-end
2. Add more sophisticated question generation (integrate OpenAI)
3. Implement revision queue UI
4. Add progress visualization charts
5. Deploy to production (consider Supabase for database)
