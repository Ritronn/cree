# Adaptive Learning System - Complete Implementation

## Overview

A comprehensive adaptive learning platform with 3 phases:
1. **Monitoring** - Track engagement, tab switches, time spent
2. **Testing** - Auto-generated quizzes from content
3. **Adaptive Learning** - ML-based difficulty adjustment

## Tech Stack

### Backend
- Django 3.1.14
- Django REST Framework 3.14.0
- SQLite (development) / Supabase (production)
- scikit-learn (Random Forest ML model)
- OpenAI API (question generation)

### Frontend
- React 18
- Vite
- Tailwind CSS
- Framer Motion
- Axios

### ML Model
- Random Forest Classifier
- 8 input features
- 3 difficulty levels (1-3)
- Rule-based fallback

## Features

### Content Support
- YouTube videos (transcript extraction)
- PDF documents
- PowerPoint presentations
- Word documents

### Monitoring
- Tab switch detection
- Focus tracking
- Time spent tracking
- Engagement metrics
- Activity logging

### Assessment
- Auto-generated questions
- Multiple difficulty levels
- Immediate feedback
- Concept-based tracking
- Spaced repetition

### Adaptive Learning
- ML-based difficulty prediction
- Performance-based progression
- Concept mastery tracking
- Personalized learning paths
- Adaptive scoring

## Quick Start

### 1. Backend Setup

```bash
# Navigate to learning directory
cd learning

# Install dependencies
pip install -r requirements.txt
pip install -r adaptive_learning_requirements.txt

# Train ML model
python adaptive_learning/train_model.py

# Run migrations
python manage.py makemigrations adaptive_learning
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start server
python manage.py runserver
```

Backend will be available at `http://localhost:8000`

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend will be available at `http://localhost:5173`

## API Documentation

### Base URL
```
http://localhost:8000/api/adaptive
```

### Authentication
- Session-based authentication
- Login required for all endpoints

### Endpoints

#### Topics
```
GET    /topics/              - List all topics
POST   /topics/              - Create topic
GET    /topics/{id}/         - Get topic
PATCH  /topics/{id}/         - Update topic
DELETE /topics/{id}/         - Delete topic
GET    /topics/{id}/progress/ - Get progress
GET    /topics/{id}/concepts/ - Get concepts
```

#### Content
```
GET    /content/                        - List content
POST   /content/upload/                 - Upload content
GET    /content/{id}/                   - Get content
POST   /content/{id}/generate_assessment/ - Generate quiz
DELETE /content/{id}/                   - Delete content
```

#### Assessments
```
GET    /assessments/                    - List assessments
GET    /assessments/{id}/               - Get assessment
GET    /assessments/{id}/questions/     - Get questions
POST   /assessments/{id}/submit_answer/ - Submit answer
POST   /assessments/{id}/complete/      - Complete assessment
```

#### Monitoring
```
POST   /monitoring/start_session/       - Start session
POST   /monitoring/{id}/track_event/    - Track event
POST   /monitoring/{id}/end_session/    - End session
```

#### Progress
```
GET    /progress/          - List progress
GET    /progress/overview/ - Get overview
```

## User Workflow

### 1. Create Topic
```javascript
const topic = await topicsAPI.create({
  name: "Python Programming",
  description: "Learn Python basics"
});
```

### 2. Upload Content
```javascript
const formData = new FormData();
formData.append('topic', topicId);
formData.append('title', 'Python Functions');
formData.append('content_type', 'youtube');
formData.append('url', 'https://youtube.com/watch?v=...');

const content = await contentAPI.upload(formData);
```

### 3. Generate Assessment
```javascript
const assessment = await contentAPI.generateAssessment(contentId);
```

### 4. Start Monitoring
```javascript
const session = await monitoringAPI.startSession(contentId);
monitoringTracker.start(session.id, (eventType, data) => {
  monitoringAPI.trackEvent(session.id, eventType, data);
});
```

### 5. Take Assessment
```javascript
// Get questions
const questions = await assessmentAPI.getQuestions(assessmentId);

// Submit answers
for (const answer of answers) {
  await assessmentAPI.submitAnswer(assessmentId, {
    question_id: answer.questionId,
    selected_answer_index: answer.selectedIndex,
    time_taken_seconds: answer.timeTaken
  });
}

// Complete and get results
const results = await assessmentAPI.complete(assessmentId);
```

### 6. View Results
```javascript
// Results include:
// - score (percentage)
// - adaptive_score (ML-calculated)
// - weak_concepts (concepts to review)
// - next_difficulty (predicted level)
// - feedback_message
```

## ML Model

### Input Features (8)
1. `accuracy` - Current accuracy (0-100)
2. `avg_time_per_question` - Average time (10-120 seconds)
3. `first_attempt_correct` - First attempt rate (0-100)
4. `current_difficulty` - Current level (1-3)
5. `sessions_completed` - Number of sessions (1-50)
6. `score_trend` - Score change (-50 to +50)
7. `mastery_level` - Mastery level (0-1)
8. `is_new_topic` - New topic flag (0 or 1)

### Output
- `next_difficulty` - Predicted difficulty (1, 2, or 3)

### Business Rules
1. New topics always start at difficulty 1
2. No skipping levels (change by ±1 only)
3. Accuracy < 50% → decrease difficulty
4. Accuracy > 85% + 2+ sessions → increase difficulty
5. Positive trend + accuracy ≥ 70% → increase
6. Negative trend → decrease

### Training
```bash
python adaptive_learning/train_model.py
```

Generates:
- `ml_models/adaptive_model.pkl` - Trained model
- `ml_models/training_data.csv` - Synthetic data

## Content Processing

### YouTube
- Uses `youtube-transcript-api`
- Extracts video transcript
- Identifies key concepts

### PDF
- Uses `PyPDF2`
- Extracts text from all pages
- Identifies key concepts

### PowerPoint
- Uses `python-pptx`
- Extracts text from slides
- Identifies key concepts

### Word
- Uses `python-docx`
- Extracts text from paragraphs
- Identifies key concepts

## Question Generation

### OpenAI (Primary)
- Uses GPT-3.5-turbo
- Generates contextual questions
- Requires `OPENAI_API_KEY` environment variable

### Template-based (Fallback)
- Uses predefined templates
- Generates questions from concepts
- No API key required

## Monitoring System

### Tracked Events
- Tab switches
- Focus lost/gained
- Time updates (every 10 seconds)
- User activity (mouse, keyboard, scroll)

### Metrics
- Total time
- Active time
- Tab switches count
- Focus lost count
- Engagement rate

### Usage
```javascript
import monitoringTracker from './utils/monitoring';

// Start tracking
monitoringTracker.start(sessionId, (eventType, data) => {
  // Send to backend
  monitoringAPI.trackEvent(sessionId, eventType, data);
});

// Get stats
const stats = monitoringTracker.getStats();

// Stop tracking
monitoringTracker.stop();
```

## Database Schema

### Models
1. **Topic** - Learning topics
2. **Content** - Learning materials
3. **Assessment** - Generated quizzes
4. **Question** - Individual questions
5. **UserAnswer** - Student responses
6. **UserProgress** - Overall progress
7. **MonitoringSession** - Engagement tracking
8. **ConceptMastery** - Concept-level tracking
9. **RevisionQueue** - Spaced repetition

### Relationships
```
User → Topic → Content → Assessment → Question → UserAnswer
     → UserProgress
     → ConceptMastery
     → MonitoringSession
     → RevisionQueue
```

## Configuration

### Django Settings
```python
INSTALLED_APPS = [
    'adaptive_learning',
    'rest_framework',
    'corsheaders',
    # ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

### Environment Variables
```bash
# Optional: For OpenAI question generation
export OPENAI_API_KEY="your-api-key-here"
```

## Testing

### Backend
```bash
# Run Django tests
python manage.py test adaptive_learning

# Test API endpoints
python test_adaptive_api.py
```

### Frontend
```bash
# Run React tests
npm test

# Build for production
npm run build
```

## Deployment

### Backend (Django)
1. Set `DEBUG = False`
2. Configure production database (Supabase)
3. Set `ALLOWED_HOSTS`
4. Collect static files: `python manage.py collectstatic`
5. Use gunicorn or uwsgi

### Frontend (React)
1. Build: `npm run build`
2. Deploy `dist/` folder to hosting (Vercel, Netlify)
3. Update API base URL in `api.js`

### Database Migration (SQLite → Supabase)
1. Export data: `python manage.py dumpdata > data.json`
2. Configure Supabase in settings
3. Run migrations
4. Import data: `python manage.py loaddata data.json`

## Troubleshooting

### CORS Errors
- Ensure Django server is running
- Check CORS_ALLOWED_ORIGINS includes frontend URL
- Verify corsheaders middleware is installed

### Authentication Errors
- Create user: `python manage.py createsuperuser`
- Login via Django admin
- Check session cookies are being sent

### File Upload Errors
- Ensure `media/` directory exists
- Check file permissions
- Verify MEDIA_ROOT and MEDIA_URL settings

### ML Model Errors
- Run `python adaptive_learning/train_model.py`
- Check `ml_models/adaptive_model.pkl` exists
- Verify joblib and scikit-learn are installed

## Performance Optimization

### Backend
- Use database indexing
- Implement caching (Redis)
- Optimize queries (select_related, prefetch_related)
- Use async views for long operations

### Frontend
- Code splitting
- Lazy loading components
- Memoization (useMemo, useCallback)
- Virtual scrolling for long lists

## Security

### Backend
- CSRF protection enabled
- SQL injection prevention (ORM)
- File upload validation
- Rate limiting (django-ratelimit)

### Frontend
- XSS prevention (React escaping)
- Secure API calls (HTTPS in production)
- Input validation
- Content Security Policy

## Future Enhancements

1. **Real-time collaboration** - WebSockets for live sessions
2. **Advanced analytics** - Charts and visualizations
3. **Mobile app** - React Native version
4. **Gamification** - Badges, achievements, leaderboards
5. **Social features** - Share progress, compete with friends
6. **Advanced ML** - Deep learning models, NLP
7. **Multi-language** - i18n support
8. **Accessibility** - WCAG compliance

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Write tests
5. Submit pull request

## License

MIT License

## Support

For issues and questions:
- GitHub Issues
- Email: support@example.com
- Discord: discord.gg/example

---

Built with ❤️ for adaptive learning
