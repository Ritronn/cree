# 🚀 Quick Start Guide - Gemini MCQ Integration

## What You Can Do Now

Your app now has **AI-powered adaptive MCQ generation** integrated! Here's what happens:

1. User pastes a YouTube URL
2. Backend fetches the transcript
3. Gemini AI generates 20 adaptive questions
4. User takes the assessment
5. Results shown with explanations

## 🎯 Try It Now!

### Step 1: Start the Servers

**Backend (if not running):**
```bash
cd learning
python manage.py runserver
```

**Frontend (if not running):**
```bash
cd frontend
npm run dev
```

### Step 2: Test the Feature

1. Open browser: `http://localhost:5173`
2. Sign in to your account
3. Go to Dashboard
4. Click "Create Session" or open an existing session
5. Click "Add Content" button (top right)
6. Select "YouTube Video"
7. Paste this test URL: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
   (Or any YouTube video with captions)
8. Click "Confirm"
9. Wait 5-10 seconds (you'll see "Processing..." message)
10. Success message appears in chat: "Content processed! 20 questions generated"
11. Click "Take Assessment (20 questions)" button
12. Answer the questions
13. Click "Submit" on the last question
14. See your results with explanations!

## 📸 What You'll See

### 1. Add Content Modal
```
┌─────────────────────────────────────┐
│  Add Content                    [X] │
├─────────────────────────────────────┤
│  [📺 YouTube Video]                 │
│  [📄 Word Document]                 │
│  [📄 PDF Document]                  │
│  [📊 PowerPoint]                    │
└─────────────────────────────────────┘
```

### 2. YouTube URL Input
```
┌─────────────────────────────────────┐
│  ← Back                             │
│                                     │
│  YouTube URL                        │
│  🔗 [https://youtube.com/watch?v=...]│
│                                     │
│  ℹ️ Transcript will be fetched and  │
│     MCQs will be generated          │
│                                     │
│  [⚡ Processing... ]                │
└─────────────────────────────────────┘
```

### 3. Success Message
```
Chat:
┌─────────────────────────────────────┐
│  🤖 Content processed successfully! │
│     20 questions generated and      │
│     ready for assessment.           │
└─────────────────────────────────────┘
```

### 4. Take Assessment Button
```
┌─────────────────────────────────────┐
│  [Video Player]                     │
│                                     │
│  [Take Assessment (20 questions)]   │
└─────────────────────────────────────┘
```

### 5. Assessment Page
```
┌─────────────────────────────────────┐
│  Question 1 of 20                   │
├─────────────────────────────────────┤
│  What is Three.js used for?         │
│                                     │
│  ○ A. 3D rendering in the browser   │
│  ○ B. Backend API development       │
│  ○ C. Database management           │
│  ○ D. CSS styling                   │
│                                     │
│  [Previous]  ●○○○○○○  [Next]        │
└─────────────────────────────────────┘
```

### 6. Results Page
```
┌─────────────────────────────────────┐
│  ✅ Assessment Complete!             │
│                                     │
│  ┌─────┐  ┌─────┐  ┌─────┐         │
│  │  15 │  │  5  │  │ 75% │         │
│  │Correct│ │Wrong│ │Score│         │
│  └─────┘  └─────┘  └─────┘         │
│                                     │
│  ✅ Q1: What is Three.js...         │
│     Your answer: A ✓                │
│     Explanation: Three.js is...     │
│                                     │
│  ❌ Q2: Which library...            │
│     Your answer: B ✗                │
│     Correct answer: C               │
│     Explanation: React is...        │
│                                     │
│  [Back to Dashboard]                │
└─────────────────────────────────────┘
```

## 🎮 User States

The system adapts questions based on user state:

| State | When to Use | Questions | Difficulty |
|-------|-------------|-----------|------------|
| 1 - Confused | User struggling | 20 | Simple/Beginner |
| 2 - Bored | User finding it easy | 20 | Challenging |
| 3 - Overloaded | User overwhelmed | 10 | Easy + Break |
| 4 - Focused | Normal state | 20 | Intermediate |

Currently set to **State 4 (Focused)** by default.

## 🔧 How It Works Behind the Scenes

```
User Action          Backend Process           Gemini AI
─────────────────────────────────────────────────────────
Paste URL     →     Fetch transcript    →    Extract content
                    (youtube-transcript-api)   
                                              ↓
Click Confirm →     Send to Gemini      →    Generate 20 MCQs
                                              
                                              ↓
Wait 5-10s    ←     Receive questions   ←    Return JSON
                                              
                                              ↓
Click "Take   →     Display questions   →    (Questions stored
Assessment"                                    in frontend)
                                              
                                              ↓
Submit        →     Calculate score     →    Show results
```

## 📊 API Endpoints Used

### 1. Upload Content
```
POST /api/adaptive/content/upload/
Body: {
  "title": "YouTube Video",
  "content_type": "youtube",
  "url": "https://youtube.com/watch?v=..."
}
Response: {
  "id": 1,
  "title": "YouTube Video",
  "transcript": "Full transcript...",
  "processed": true
}
```

### 2. Generate MCQs
```
POST /api/adaptive/content/{id}/generate_gemini_mcqs/
Body: {
  "user_state": 4
}
Response: {
  "content_id": 1,
  "user_state": "focused",
  "difficulty": "intermediate-to-advanced",
  "num_questions": 20,
  "questions": [...]
}
```

## 🎨 Customization

### Change User State
In `frontend/src/pages/TopicWindow.jsx`, line ~280:
```javascript
const mcqResponse = await contentAPI.generateGeminiMCQs(contentId, 4);
// Change 4 to: 1 (confused), 2 (bored), 3 (overloaded), or 4 (focused)
```

### Change Number of Questions
In `learning/adaptive_learning/gemini_mcq_service.py`, line ~20-40:
```python
USER_STATE_CONFIG = {
    1: {"num_questions": 20, ...},  # Change 20 to desired number
    2: {"num_questions": 20, ...},
    3: {"num_questions": 10, ...},
    4: {"num_questions": 20, ...},
}
```

### Change Gemini Model
In `learning/adaptive_learning/gemini_mcq_service.py`, line ~15:
```python
model = genai.GenerativeModel("gemini-2.5-flash-preview-04-17")
# Change to: "gemini-pro", "gemini-1.5-pro", etc.
```

## 🐛 Common Issues

### "No transcript available"
- Video doesn't have captions
- Try a different video
- Check video URL is correct

### "MCQ generation failed"
- Check Gemini API key is valid
- Check internet connection
- Try a shorter video

### Button stays disabled
- Wait for success message in chat
- Check browser console for errors
- Refresh page and try again

### Questions not showing
- Make sure you clicked "Confirm"
- Wait for processing to complete
- Check network tab for API errors

## 📝 Files You Can Modify

### Frontend:
- `frontend/src/pages/TopicWindow.jsx` - Main study session page
- `frontend/src/pages/Assessment.jsx` - MCQ display page
- `frontend/src/services/api.js` - API calls

### Backend:
- `learning/adaptive_learning/gemini_mcq_service.py` - MCQ generation logic
- `learning/adaptive_learning/views.py` - API endpoints
- `learning/learning/settings.py` - Configuration

## 🎉 That's It!

You now have a fully working AI-powered MCQ generation system integrated into your app. Users can paste any YouTube URL and get adaptive questions generated automatically!

**Enjoy! 🚀**
