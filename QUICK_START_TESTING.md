# Quick Start Testing Guide

## Prerequisites

1. Python 3.10+ installed
2. Node.js 16+ installed
3. Grok AI API key

## Setup (First Time Only)

### 1. Backend Setup

```bash
cd learning

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env

# Edit .env and add your Grok API key:
# XAI_API_KEY=your_grok_api_key_here

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

## Running the Application

### Terminal 1: Backend
```bash
cd learning
venv\Scripts\activate  # Windows
python manage.py runserver
```

Backend will run on: http://localhost:8000

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```

Frontend will run on: http://localhost:5173

## Testing the Complete Flow

### 1. Sign Up / Sign In
1. Open http://localhost:5173
2. Click "Sign Up"
3. Fill in details and create account
4. Sign in with your credentials

### 2. Dashboard
- You'll see the new dashboard with:
  - Completion bar at top (0% initially)
  - Stats cards (sessions today, study time, pending tests, weak points)
  - "Create New Study Session" button
  - Empty weekly sessions grid

### 3. Create Study Session
1. Click "Create New Study Session"
2. Enter workspace name: "Python Basics Study"
3. Select session type:
   - **Recommended**: 2 hours + 20 min break
   - **Standard**: 50 minutes + 10 min break
   - **Custom**: Your choice
4. Upload a PDF/DOCX/PPT file (any educational content)
5. Click "Start Study Session"

### 4. Study Session Window
- Content will be displayed
- Session timer starts
- Camera monitoring (if enabled)
- You can:
  - Take breaks
  - Use whiteboard
  - Chat with AI
  - End session anytime

### 5. End Session & Generate Test
1. Click "End Session" button
2. Backend will:
   - Process the content with Grok AI
   - Generate 20-25 questions
   - Set 6-hour expiry for test
3. You'll be redirected to dashboard

### 6. Take Test
1. Dashboard shows pending test with countdown
2. Click "Take Test" button
3. AMCAT-style test window opens:
   - **Left panel**: Questions and answers
   - **Right top**: Camera feed (must allow camera)
   - **Right bottom**: Question navigator
4. Answer questions:
   - MCQ: Click option
   - Short Answer: Type answer
   - Problem Solving: Type detailed solution
5. Navigate using Previous/Next or click question numbers
6. Question navigator shows:
   - Green: Answered
   - Red: Not answered
   - Pink: Current question
7. Timer counts down at top
8. Click "Submit Test" when done

### 7. Test Results
1. Test is auto-graded
2. Email sent with results (check console if no email service)
3. Weak points identified (<70% accuracy)
4. Dashboard updated:
   - Completion percentage increases
   - Test marked as completed
   - Session limit updated

### 8. View Recommendations
1. Go to weak points section
2. See recommended:
   - YouTube playlists
   - Articles
   - Stack Overflow questions
3. Click to view resources

## Session Limits

- **Maximum 3 sessions per day**
- Cannot create new session if:
  - Already created 3 today
  - Have pending tests from previous sessions
- Complete pending tests to unlock new sessions

## Test Expiry

- Tests expire 6 hours after session ends
- Expired tests cannot be taken
- Must create new session to get new test

## Browser Extension (Optional)

1. Open Chrome
2. Go to `chrome://extensions/`
3. Enable "Developer mode"
4. Click "Load unpacked"
5. Select `browser-extension` folder
6. Extension will track:
   - Tab switches
   - Blocked sites
   - Focus time

## Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Kill process on port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:8000 | xargs kill -9
```

**Database errors:**
```bash
# Delete database and recreate
del db.sqlite3
python manage.py migrate
```

**Grok AI errors:**
- Check XAI_API_KEY in .env
- Verify API key is valid
- Check internet connection

### Frontend Issues

**Module not found:**
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**Port already in use:**
```bash
# Kill process on port 5173
# Windows:
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:5173 | xargs kill -9
```

**CORS errors:**
- Backend must be running on port 8000
- Frontend must be running on port 5173
- Check browser console for details

### Camera Issues

**Camera not working in test window:**
- Allow camera permission in browser
- Check if camera is being used by another app
- Try different browser
- Check browser console for errors

### Email Issues

**Emails not sending:**
- Check console logs (fallback mode)
- Add SENDGRID_API_KEY or MAILGUN_API_KEY to .env
- Verify API keys are valid
- Check spam folder

## API Endpoints

### Authentication
- POST `/accounts/api/register/` - Sign up
- POST `/accounts/api/login/` - Sign in
- POST `/accounts/api/logout/` - Sign out

### Dashboard
- GET `/api/adaptive/dashboard/overview/` - Dashboard data

### Sessions
- POST `/api/adaptive/study-sessions/` - Create session
- GET `/api/adaptive/study-sessions/{id}/status/` - Session status
- POST `/api/adaptive/study-sessions/{id}/complete/` - End session

### Tests
- GET `/api/adaptive/tests/{id}/` - Get test with questions
- POST `/api/adaptive/tests/{id}/start/` - Start test timer
- POST `/api/adaptive/tests/{id}/submit_answer/` - Submit answer
- POST `/api/adaptive/tests/{id}/complete/` - Complete test

### Weak Points
- GET `/api/adaptive/weak-points/` - List weak points
- GET `/api/adaptive/weak-points/recommendations/` - Get recommendations

### Browser Extension
- POST `/api/adaptive/extension/heartbeat/` - Extension heartbeat
- POST `/api/adaptive/extension/violation/` - Log violation
- GET `/api/adaptive/extension/status/` - Extension status

## Expected Behavior

### Session Creation
✅ Can create up to 3 sessions per day
✅ Blocked if pending tests exist
✅ Workspace name is required
✅ File upload is required
✅ Session type selection is required

### Test Generation
✅ Automatically generated on session completion
✅ 20-25 questions based on difficulty
✅ Mix of MCQ, Short Answer, Problem Solving
✅ 6-hour expiry from session end

### Test Taking
✅ Camera monitoring required
✅ Timer countdown
✅ Auto-submit on timeout
✅ Question navigator with color coding
✅ Can navigate freely between questions

### Test Results
✅ Immediate grading
✅ Email with detailed results
✅ Weak points identified
✅ Recommendations generated
✅ Dashboard updated

### Completion Tracking
✅ Percentage = (completed tests / total sessions) * 100
✅ Updates in real-time
✅ Shows in progress bar

## Demo Data

For quick testing, you can use these sample files:
- Any PDF document
- Any Word document
- Any PowerPoint presentation

The system will extract text and generate questions based on the content.

## Support

If you encounter issues:
1. Check console logs (browser and terminal)
2. Verify all services are running
3. Check API endpoints are responding
4. Review error messages
5. Check database for data

## Next Steps

After testing the basic flow:
1. Test session limits (create 3 sessions)
2. Test pending test blocking
3. Test test expiry (wait 6 hours or modify code)
4. Test weak point recommendations
5. Test browser extension integration
6. Test email delivery
7. Test camera monitoring
8. Test different question types

Enjoy testing! 🚀
