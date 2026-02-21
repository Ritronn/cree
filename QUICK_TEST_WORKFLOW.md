# Quick Test Workflow Guide

## Complete End-to-End Testing

This guide will walk you through testing the entire Velocity platform from start to finish.

## Prerequisites

1. **Backend Running**:
   ```bash
   cd learning
   python manage.py runserver
   ```
   Should be accessible at `http://localhost:8000`

2. **Frontend Running**:
   ```bash
   cd frontend
   npm run dev
   ```
   Should be accessible at `http://localhost:5173`

3. **Database Migrated**:
   ```bash
   cd learning
   python manage.py migrate
   ```

## Test Workflow

### Step 1: Landing Page
1. Open `http://localhost:5173`
2. You should see the landing page with:
   - Hero section with "Learn at your own velocity"
   - Feature cards
   - How it works section
   - CTA buttons

**Test**: Click "Get Started Free" → Should navigate to `/signup`

### Step 2: Sign Up (Mock)
1. Fill in the sign-up form:
   - Name: Test User
   - Email: test@example.com
   - Password: password123

2. Click "Create Account"

**Expected**: Navigate to `/dashboard`

**Note**: Currently mocked - will navigate without actual authentication

### Step 3: Dashboard - Create Topic
1. You should see an empty dashboard with "Begin Your Journey"
2. Click "Create Your First Topic"
3. Fill in the modal:
   - Topic Name: "Python Programming"
   - Description: "Learn Python basics"
4. Click "Create Topic"

**Expected**: 
- Topic card appears in dashboard
- Navigate to `/topic/:topicId`

### Step 4: Topic Window - Add Content
1. Click "Add Content" button in header
2. Select "YouTube Video"
3. Paste a YouTube URL (e.g., `https://www.youtube.com/watch?v=dQw4w9WgXcQ`)
4. Click "Confirm"

**Expected**:
- Video appears in left sidebar under "Videos"
- Video player shows in main content area
- Can play the video

**Alternative**: Try uploading a PDF:
1. Click "Add Content" → "PDF Document"
2. Select a PDF file
3. PDF should appear in sidebar and be viewable

### Step 5: Start Study Session (Backend Integration)
1. With content selected, click "Take Assessment" or create a study session
2. This should call the backend API to create a session

**Backend API Call**:
```bash
curl -X POST http://localhost:8000/api/adaptive/study-sessions/ \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": 1,
    "session_type": "recommended"
  }'
```

**Expected Response**:
```json
{
  "session": {
    "id": 1,
    "content_id": 1,
    "session_type": "recommended",
    "started_at": "2024-01-01T00:00:00Z",
    "camera_enabled": false
  },
  "proctoring_config": {
    "enabled": true,
    "features": ["tab_switch", "copy_paste", "focus_tracking"]
  }
}
```

**Frontend**: Navigate to `/session/1`

### Step 6: Study Session Page
1. You should see:
   - Content viewer (video/PDF)
   - Session timer in header
   - Camera toggle button
   - Break button
   - Complete button
   - Whiteboard on right side
   - Chat interface below whiteboard

2. **Test Monitoring**:
   - Switch tabs → Should increment "Tab Switches" counter
   - Try to copy text → Should increment "Copy Attempts"
   - Click away from window → Should increment "Focus Lost"

3. **Test Camera**:
   - Click camera icon → Should toggle between on/off

4. **Test Break**:
   - Click "Break" button
   - Should show break timer
   - Content area shows "Break Time" message
   - Click "End Break Early" to resume

5. **Test Chat**:
   - Type a question in chat input
   - Click send
   - Should see your message and AI response

6. **Test Whiteboard**:
   - Draw on the whiteboard
   - Should be able to save snapshots

### Step 7: Complete Session & Generate Test
1. Click "Complete" button
2. Backend should:
   - End monitoring session
   - Calculate session metrics
   - Generate a test based on content

**Backend API Call**:
```bash
curl -X POST http://localhost:8000/api/adaptive/study-sessions/1/complete/ \
  -H "Content-Type: application/json"
```

**Expected Response**:
```json
{
  "session_id": 1,
  "completed_at": "2024-01-01T01:00:00Z",
  "total_time_seconds": 3600,
  "test": {
    "id": 1,
    "difficulty_level": 1,
    "total_questions": 10
  }
}
```

**Frontend**: Navigate to `/test/1`

### Step 8: Take Test
1. You should see:
   - Test header with timer
   - Progress bar
   - Current question
   - Answer options (MCQ) or text area (short answer)
   - Navigation buttons
   - Question navigator at bottom

2. **Answer Questions**:
   - Select/type answers for each question
   - Click "Next" to move forward
   - Click "Previous" to go back
   - Use question navigator to jump to specific questions

3. **Submit Test**:
   - Answer all questions (or skip some)
   - Click "Submit Test" on last question
   - Confirm submission

**Backend API Calls**:
```bash
# For each answer
curl -X POST http://localhost:8000/api/adaptive/tests/1/submit_answer/ \
  -H "Content-Type: application/json" \
  -d '{
    "question_id": 1,
    "selected_index": 2,
    "time_taken_seconds": 45
  }'

# Complete test
curl -X POST http://localhost:8000/api/adaptive/tests/1/complete/ \
  -H "Content-Type: application/json"
```

**Expected Response**:
```json
{
  "test_id": 1,
  "overall_score": 85.0,
  "total_questions": 10,
  "answered_questions": 10,
  "correct_answers": 8,
  "weak_areas": [
    {
      "concept": "Variables",
      "accuracy": 60.0
    }
  ],
  "next_difficulty": 2,
  "difficulty_feedback": "Great job! Moving up to difficulty level 2."
}
```

### Step 9: View Results
1. You should see:
   - Trophy icon with celebration
   - Overall score percentage
   - Score card with:
     - Correct answers count
     - Time taken
     - Next difficulty level
   - Feedback message
   - Weak areas to improve
   - Action buttons

2. **Test Actions**:
   - Click "Back to Dashboard" → Navigate to `/dashboard`
   - Click "Take Another Test" → Reload test page

### Step 10: Dashboard - View Progress
1. Back on dashboard, you should see:
   - Topic card with updated mastery percentage
   - Content count
   - Progress bar showing improvement

2. **Test Progress API**:
```bash
curl http://localhost:8000/api/adaptive/topics/1/progress/
```

**Expected Response**:
```json
{
  "topic_id": 1,
  "mastery_level": 0.85,
  "total_assessments": 1,
  "average_accuracy": 85.0,
  "last_session_at": "2024-01-01T01:00:00Z",
  "score_trend": 0
}
```

## Backend API Testing

### Test All Endpoints

1. **Topics**:
```bash
# List topics
curl http://localhost:8000/api/adaptive/topics/

# Create topic
curl -X POST http://localhost:8000/api/adaptive/topics/ \
  -H "Content-Type: application/json" \
  -d '{"name": "JavaScript", "description": "Learn JS"}'

# Get topic progress
curl http://localhost:8000/api/adaptive/topics/1/progress/

# Get concept mastery
curl http://localhost:8000/api/adaptive/topics/1/concepts/
```

2. **Content**:
```bash
# Upload YouTube content
curl -X POST http://localhost:8000/api/adaptive/content/upload/ \
  -F "topic=1" \
  -F "title=Python Tutorial" \
  -F "content_type=youtube" \
  -F "url=https://youtube.com/watch?v=..."

# Generate assessment
curl -X POST http://localhost:8000/api/adaptive/content/1/generate_assessment/
```

3. **Assessments**:
```bash
# Get assessment questions
curl http://localhost:8000/api/adaptive/assessments/1/questions/

# Submit answer
curl -X POST http://localhost:8000/api/adaptive/assessments/1/submit_answer/ \
  -H "Content-Type: application/json" \
  -d '{
    "question_id": 1,
    "selected_answer_index": 2,
    "time_taken_seconds": 45
  }'

# Complete assessment
curl -X POST http://localhost:8000/api/adaptive/assessments/1/complete/
```

4. **Study Sessions**:
```bash
# Create session
curl -X POST http://localhost:8000/api/adaptive/study-sessions/ \
  -H "Content-Type: application/json" \
  -d '{"content_id": 1, "session_type": "recommended"}'

# Get session status
curl http://localhost:8000/api/adaptive/study-sessions/1/status/

# Start break
curl -X POST http://localhost:8000/api/adaptive/study-sessions/1/start_break/

# End break
curl -X POST http://localhost:8000/api/adaptive/study-sessions/1/end_break/

# Complete session
curl -X POST http://localhost:8000/api/adaptive/study-sessions/1/complete/
```

5. **Monitoring**:
```bash
# Record event
curl -X POST http://localhost:8000/api/adaptive/session-monitoring/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": 1,
    "event_type": "video_pause",
    "event_data": {"position": 120}
  }'
```

6. **Proctoring**:
```bash
# Record tab switch
curl -X POST http://localhost:8000/api/adaptive/proctoring/ \
  -H "Content-Type: application/json" \
  -d '{"session_id": 1, "event_type": "tab_switch"}'

# Record copy attempt
curl -X POST http://localhost:8000/api/adaptive/proctoring/ \
  -H "Content-Type: application/json" \
  -d '{"session_id": 1, "event_type": "copy_attempt"}'
```

7. **Tests**:
```bash
# Generate test
curl -X POST http://localhost:8000/api/adaptive/tests/generate/ \
  -H "Content-Type: application/json" \
  -d '{"session_id": 1, "difficulty": 1}'

# Start test
curl -X POST http://localhost:8000/api/adaptive/tests/1/start/

# Submit answer
curl -X POST http://localhost:8000/api/adaptive/tests/1/submit_answer/ \
  -H "Content-Type: application/json" \
  -d '{
    "question_id": 1,
    "answer_text": "My answer",
    "time_taken_seconds": 60
  }'

# Complete test
curl -X POST http://localhost:8000/api/adaptive/tests/1/complete/
```

8. **Chat**:
```bash
# Send query
curl -X POST http://localhost:8000/api/adaptive/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": 1,
    "query": "Explain variables",
    "context": "Python Programming"
  }'

# Get history
curl "http://localhost:8000/api/adaptive/chat/history/?session_id=1"
```

## Common Issues & Solutions

### Issue: CORS Errors
**Solution**: Ensure Django settings have:
```python
CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]
CORS_ALLOW_CREDENTIALS = True
```

### Issue: 404 Not Found
**Solution**: 
- Check backend is running on port 8000
- Verify API base URL in `frontend/src/services/api.js`
- Check Django URL patterns

### Issue: Content Not Processing
**Solution**:
- Check Django logs for errors
- Verify content processor is working
- Ensure required packages are installed

### Issue: Test Not Generating
**Solution**:
- Check if content is processed
- Verify question generator is working
- Check Django logs for errors

### Issue: Monitoring Not Working
**Solution**:
- Check browser console for errors
- Verify monitoring utility is initialized
- Check network tab for API calls

## Performance Testing

### Load Testing
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test topic creation
ab -n 100 -c 10 -p topic.json -T application/json \
  http://localhost:8000/api/adaptive/topics/

# Test content upload
ab -n 50 -c 5 -p content.json -T application/json \
  http://localhost:8000/api/adaptive/content/upload/
```

### Frontend Performance
1. Open Chrome DevTools
2. Go to Lighthouse tab
3. Run audit
4. Check:
   - Performance score
   - Accessibility score
   - Best practices score

## Success Criteria

✅ **Complete Workflow**:
- [ ] Can create topics
- [ ] Can upload content (YouTube, PDF)
- [ ] Can start study sessions
- [ ] Monitoring tracks events
- [ ] Proctoring detects violations
- [ ] Can use whiteboard
- [ ] Can chat with AI
- [ ] Can complete sessions
- [ ] Tests are generated
- [ ] Can take and submit tests
- [ ] Results are displayed
- [ ] Progress is tracked

✅ **Backend Integration**:
- [ ] All API endpoints respond correctly
- [ ] Data is persisted to database
- [ ] ML predictions work
- [ ] Content processing works
- [ ] Question generation works

✅ **Frontend Features**:
- [ ] All pages render correctly
- [ ] Navigation works
- [ ] Forms submit properly
- [ ] Real-time updates work
- [ ] Error handling works

## Next Steps After Testing

1. **Fix any bugs found during testing**
2. **Add authentication integration**
3. **Implement real-time features with WebSockets**
4. **Add more comprehensive error handling**
5. **Optimize performance**
6. **Add unit and integration tests**
7. **Prepare for deployment**

## Support

If you encounter issues:
1. Check browser console for errors
2. Check Django server logs
3. Review network tab in DevTools
4. Refer to `FRONTEND_BACKEND_INTEGRATION_COMPLETE.md`
5. Check individual component documentation

## Summary

You now have a complete, integrated adaptive learning platform with:
- Topic and content management
- Study session monitoring
- Proctoring system
- Adaptive testing
- Progress tracking
- Whiteboard and chat features

Test the complete workflow and report any issues!
