# Frontend-Backend Integration Complete Guide

## Overview
This document describes the complete integration between the React frontend and Django backend for the Velocity adaptive learning platform.

## Architecture

### Backend (Django REST Framework)
- **Base URL**: `http://localhost:8000/api/adaptive/`
- **Authentication**: Session-based with CSRF tokens
- **API Style**: RESTful with ViewSets

### Frontend (React + Vite)
- **Base URL**: `http://localhost:5173/`
- **State Management**: React Hooks
- **HTTP Client**: Axios with interceptors

## API Endpoints Integration

### 1. Topics Management
**Backend**: `TopicViewSet` in `adaptive_learning/views.py`
**Frontend**: `topicsAPI` in `frontend/src/services/api.js`

```javascript
// Create topic
const topic = await topicsAPI.create({ name: 'Python', description: 'Learn Python' });

// List topics
const topics = await topicsAPI.list();

// Get topic progress
const progress = await topicsAPI.getProgress(topicId);

// Get concept mastery
const concepts = await topicsAPI.getConcepts(topicId);
```

### 2. Content Management
**Backend**: `ContentViewSet` in `adaptive_learning/views.py`
**Frontend**: `contentAPI` in `frontend/src/services/api.js`

```javascript
// Upload content
const formData = new FormData();
formData.append('topic', topicId);
formData.append('title', 'My Video');
formData.append('content_type', 'youtube');
formData.append('url', 'https://youtube.com/watch?v=...');
const content = await contentAPI.upload(formData);

// Generate assessment
const assessment = await contentAPI.generateAssessment(contentId);
```

### 3. Assessment System
**Backend**: `AssessmentViewSet` in `adaptive_learning/views.py`
**Frontend**: `assessmentAPI` in `frontend/src/services/api.js`

```javascript
// Get assessment questions
const questions = await assessmentAPI.getQuestions(assessmentId);

// Submit answer
await assessmentAPI.submitAnswer(assessmentId, {
  question_id: questionId,
  selected_answer_index: 2,
  time_taken_seconds: 45
});

// Complete assessment
const results = await assessmentAPI.complete(assessmentId);
```

### 4. Study Sessions
**Backend**: `StudySessionViewSet` in `adaptive_learning/study_session_views.py`
**Frontend**: `studySessionAPI` in `frontend/src/services/api.js`

```javascript
// Create session
const session = await studySessionAPI.create({
  content_id: contentId,
  session_type: 'recommended'
});

// Get session status
const status = await studySessionAPI.getStatus(sessionId);

// Start/end break
await studySessionAPI.startBreak(sessionId);
await studySessionAPI.endBreak(sessionId);

// Complete session
const result = await studySessionAPI.complete(sessionId);
```

### 5. Monitoring & Proctoring
**Backend**: `MonitoringViewSet`, `ProctoringViewSet` in `adaptive_learning/study_session_views.py`
**Frontend**: `sessionMonitoringAPI`, `proctoringAPI` in `frontend/src/services/api.js`

```javascript
// Record monitoring event
await sessionMonitoringAPI.recordEvent(sessionId, 'video_pause', {
  timestamp: Date.now(),
  position: 120
});

// Record proctoring violations
await proctoringAPI.recordTabSwitch(sessionId);
await proctoringAPI.recordCopyAttempt(sessionId);
await proctoringAPI.recordFocusLost(sessionId);
```

### 6. Testing System
**Backend**: `TestViewSet` in `adaptive_learning/study_session_views.py`
**Frontend**: `testAPI` in `frontend/src/services/api.js`

```javascript
// Generate test
const test = await testAPI.generate(sessionId, difficulty);

// Start test
await testAPI.start(testId);

// Submit answer
await testAPI.submitAnswer(testId, {
  question_id: questionId,
  answer_text: 'My answer',
  selected_index: null,
  time_taken_seconds: 60
});

// Complete test
const results = await testAPI.complete(testId);
```

### 7. Whiteboard & Chat
**Backend**: `WhiteboardViewSet`, `ChatViewSet` in `adaptive_learning/study_session_views.py`
**Frontend**: `whiteboardAPI`, `chatAPI` in `frontend/src/services/api.js`

```javascript
// Save whiteboard snapshot
await whiteboardAPI.save(sessionId, imageDataBase64, 'My notes');

// Send chat query
const response = await chatAPI.sendQuery(sessionId, 'Explain this concept', context);

// Get chat history
const history = await chatAPI.getHistory(sessionId);
```

## Frontend Pages

### 1. Landing Page (`/`)
- **Component**: `frontend/src/pages/Landing.jsx`
- **Features**: Hero section, features showcase, how it works
- **Backend Integration**: None (static marketing page)

### 2. Sign Up (`/signup`)
- **Component**: `frontend/src/pages/SignUp.jsx`
- **Features**: User registration form
- **Backend Integration**: TODO - Connect to Django authentication

### 3. Sign In (`/signin`)
- **Component**: `frontend/src/pages/SignIn.jsx`
- **Features**: User login form
- **Backend Integration**: TODO - Connect to Django authentication

### 4. Dashboard (`/dashboard`)
- **Component**: `frontend/src/pages/Dashboard.jsx`
- **Features**: Topic list, create topic, progress overview
- **Backend Integration**:
  - Load topics: `topicsAPI.list()`
  - Create topic: `topicsAPI.create()`
  - View progress: `topicsAPI.getProgress()`

### 5. Topic Window (`/topic/:topicId`)
- **Component**: `frontend/src/pages/TopicWindow.jsx`
- **Features**: Content management, whiteboard, chat
- **Backend Integration**:
  - Upload content: `contentAPI.upload()`
  - List content: `contentAPI.list()`
  - Generate assessment: `contentAPI.generateAssessment()`
  - Chat: `chatAPI.sendQuery()`

### 6. Study Session (`/session/:sessionId`)
- **Component**: `frontend/src/pages/StudySession.jsx`
- **Features**: Content viewing, monitoring, proctoring, whiteboard, chat
- **Backend Integration**:
  - Session management: `studySessionAPI.*`
  - Monitoring: `sessionMonitoringAPI.recordEvent()`
  - Proctoring: `proctoringAPI.*`
  - Chat: `chatAPI.sendQuery()`
  - Whiteboard: `whiteboardAPI.save()`

### 7. Test (`/test/:testId`)
- **Component**: `frontend/src/pages/Test.jsx`
- **Features**: Take test, submit answers, view results
- **Backend Integration**:
  - Load test: `testAPI.get()`
  - Start test: `testAPI.start()`
  - Submit answers: `testAPI.submitAnswer()`
  - Complete test: `testAPI.complete()`

### 8. Learning Window (`/learning/:contentId`)
- **Component**: `frontend/src/pages/LearningWindow.jsx`
- **Features**: Content viewing, assessment taking
- **Backend Integration**:
  - Load content: `contentAPI.get()`
  - Load assessment: `assessmentAPI.get()`
  - Submit answers: `assessmentAPI.submitAnswer()`
  - Complete assessment: `assessmentAPI.complete()`

## Client-Side Monitoring

### Monitoring Utility (`frontend/src/utils/monitoring.js`)

The monitoring utility provides client-side tracking of user behavior:

```javascript
import { initializeMonitoring, trackEvent } from '../utils/monitoring';

// Initialize monitoring for a session
initializeMonitoring(sessionId, {
  onTabSwitch: () => console.log('Tab switched'),
  onCopyAttempt: () => console.log('Copy attempted'),
  onFocusLost: () => console.log('Focus lost')
});

// Track custom events
trackEvent(sessionId, 'video_pause', { position: 120 });
trackEvent(sessionId, 'question_answered', { questionId: 1, correct: true });
```

**Features**:
- Tab switch detection
- Copy/paste attempt detection
- Focus lost/gained tracking
- Mouse movement tracking
- Keyboard activity tracking
- Idle time detection
- Custom event tracking

## Data Flow Examples

### Complete Learning Workflow

1. **User creates a topic**
   ```
   Frontend: Dashboard → Create Topic Button
   API Call: topicsAPI.create({ name, description })
   Backend: TopicViewSet.create()
   Response: Topic object with ID
   ```

2. **User uploads content**
   ```
   Frontend: TopicWindow → Add Content Modal
   API Call: contentAPI.upload(formData)
   Backend: ContentViewSet.upload() → process_content()
   Response: Content object with processed flag
   ```

3. **User starts study session**
   ```
   Frontend: TopicWindow → Start Session Button
   API Call: studySessionAPI.create({ content_id })
   Backend: StudySessionViewSet.create() → SessionManager.create_session()
   Response: Session object with proctoring config
   Navigate to: /session/:sessionId
   ```

4. **During study session**
   ```
   Frontend: StudySession → User watches content
   Monitoring: Track events (tab switches, focus, time)
   API Calls: sessionMonitoringAPI.recordEvent()
   Backend: MonitoringCollector.record_event()
   ```

5. **User completes session**
   ```
   Frontend: StudySession → Complete Button
   API Call: studySessionAPI.complete(sessionId)
   Backend: SessionManager.complete_session() → TestGenerator.generate_test()
   Response: Session completion data + generated test
   Navigate to: /test/:testId
   ```

6. **User takes test**
   ```
   Frontend: Test → Answer questions
   API Calls: testAPI.submitAnswer() for each question
   Backend: AssessmentEngine.evaluate_*()
   Final: testAPI.complete()
   Backend: AssessmentEngine.calculate_test_score()
   Response: Test results with next difficulty
   ```

7. **View progress**
   ```
   Frontend: Dashboard → View Progress
   API Call: progressAPI.getOverview()
   Backend: ProgressViewSet.overview()
   Response: Aggregated progress metrics
   ```

## Setup Instructions

### Backend Setup

1. **Install dependencies**:
   ```bash
   cd learning
   pip install -r requirements.txt
   pip install -r adaptive_learning_requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

5. **Start server**:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Configure API base URL**:
   Edit `frontend/src/services/api.js`:
   ```javascript
   const api = axios.create({
     baseURL: 'http://localhost:8000/api/adaptive',
     // ...
   });
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

4. **Access application**:
   Open `http://localhost:5173` in your browser

## Testing the Integration

### 1. Test Topic Creation
```bash
# Backend
curl -X POST http://localhost:8000/api/adaptive/topics/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Topic", "description": "Test"}'

# Frontend
# Navigate to /dashboard and click "Create Topic"
```

### 2. Test Content Upload
```bash
# Backend
curl -X POST http://localhost:8000/api/adaptive/content/upload/ \
  -F "topic=1" \
  -F "title=Test Video" \
  -F "content_type=youtube" \
  -F "url=https://youtube.com/watch?v=dQw4w9WgXcQ"

# Frontend
# Navigate to /topic/1 and click "Add Content"
```

### 3. Test Study Session
```bash
# Backend
curl -X POST http://localhost:8000/api/adaptive/study-sessions/ \
  -H "Content-Type: application/json" \
  -d '{"content_id": 1, "session_type": "recommended"}'

# Frontend
# Navigate to /topic/1, select content, click "Start Session"
```

### 4. Test Assessment
```bash
# Backend
curl -X POST http://localhost:8000/api/adaptive/content/1/generate_assessment/

# Frontend
# Navigate to /learning/1 and click "Start Assessment"
```

## CORS Configuration

Ensure Django is configured to allow requests from the frontend:

```python
# learning/learning/settings.py

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
```

## Authentication Integration (TODO)

Currently, authentication is mocked in the frontend. To integrate with Django:

1. **Update Sign In**:
   ```javascript
   // frontend/src/pages/SignIn.jsx
   const handleSubmit = async (e) => {
     e.preventDefault();
     try {
       const response = await axios.post('/api/accounts/login/', {
         email: formData.email,
         password: formData.password
       });
       // Store session/token
       navigate('/dashboard');
     } catch (err) {
       setError('Invalid credentials');
     }
   };
   ```

2. **Update Sign Up**:
   ```javascript
   // frontend/src/pages/SignUp.jsx
   const handleSubmit = async (e) => {
     e.preventDefault();
     try {
       await axios.post('/api/accounts/register/', {
         name: formData.name,
         email: formData.email,
         password: formData.password
       });
       navigate('/signin');
     } catch (err) {
       setError('Registration failed');
     }
   };
   ```

3. **Add Protected Routes**:
   ```javascript
   // frontend/src/components/ProtectedRoute.jsx
   import { Navigate } from 'react-router-dom';
   
   export default function ProtectedRoute({ children }) {
     const isAuthenticated = checkAuth(); // Implement this
     return isAuthenticated ? children : <Navigate to="/signin" />;
   }
   ```

## Error Handling

### Backend Errors
All API endpoints return consistent error responses:
```json
{
  "error": "Error message",
  "details": "Additional details"
}
```

### Frontend Error Handling
```javascript
try {
  const response = await api.get('/endpoint/');
  // Handle success
} catch (error) {
  if (error.response) {
    // Server responded with error
    console.error('Error:', error.response.data.error);
  } else if (error.request) {
    // Request made but no response
    console.error('Network error');
  } else {
    // Something else happened
    console.error('Error:', error.message);
  }
}
```

## Performance Optimization

### Backend
- Use `select_related()` and `prefetch_related()` for database queries
- Implement caching for frequently accessed data
- Use pagination for large datasets

### Frontend
- Implement lazy loading for routes
- Use React.memo() for expensive components
- Debounce API calls for search/filter operations
- Cache API responses with React Query or SWR

## Next Steps

1. **Complete Authentication Integration**
   - Connect Sign In/Sign Up to Django backend
   - Implement JWT or session-based auth
   - Add protected routes

2. **Add Real-time Features**
   - WebSocket integration for live monitoring
   - Real-time chat updates
   - Live proctoring alerts

3. **Enhance UI/UX**
   - Add loading skeletons
   - Improve error messages
   - Add success notifications
   - Implement dark/light theme toggle

4. **Testing**
   - Write unit tests for API functions
   - Add integration tests for workflows
   - Implement E2E tests with Cypress

5. **Deployment**
   - Configure production settings
   - Set up CI/CD pipeline
   - Deploy to cloud platform

## Troubleshooting

### CORS Errors
- Check `CORS_ALLOWED_ORIGINS` in Django settings
- Ensure `withCredentials: true` in axios config
- Verify frontend URL matches allowed origins

### 404 Errors
- Check API base URL in `api.js`
- Verify Django URL patterns
- Ensure backend server is running

### Authentication Errors
- Check CSRF token handling
- Verify session cookie settings
- Ensure credentials are being sent

### Data Not Loading
- Check network tab in browser DevTools
- Verify API endpoint responses
- Check for JavaScript console errors

## Support

For issues or questions:
1. Check this documentation
2. Review backend API documentation
3. Check browser console for errors
4. Review Django server logs
5. Create an issue in the repository

## Summary

The frontend and backend are now fully integrated with:
- ✅ Complete API service layer
- ✅ All CRUD operations for topics, content, assessments
- ✅ Study session management
- ✅ Monitoring and proctoring
- ✅ Testing system
- ✅ Whiteboard and chat integration
- ✅ Client-side monitoring utilities
- ✅ Comprehensive error handling
- ⏳ Authentication (needs completion)
- ⏳ Real-time features (optional enhancement)

The application is ready for testing the complete workflow from topic creation to test completion!
