# Gemini MCQ Integration Guide

## Overview
This integration adds AI-powered adaptive MCQ generation using Google's Gemini API. The system automatically:
1. Fetches YouTube transcripts
2. Extracts technical/educational content
3. Generates adaptive MCQs based on user state
4. Returns questions for assessment

## Architecture

### Flow:
```
User pastes YouTube URL
    ↓
Backend fetches transcript (youtube-transcript-api)
    ↓
Transcript sent to Gemini AI
    ↓
Gemini extracts technical content
    ↓
Gemini generates adaptive MCQs
    ↓
Questions returned to frontend
    ↓
User takes assessment
```

## API Endpoints

### 1. Upload Content (Existing - Enhanced)
**POST** `/api/adaptive/content/upload/`

**Request:**
```json
{
  "title": "3D Avatar Builder Tutorial",
  "content_type": "youtube",
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Response:**
```json
{
  "id": 1,
  "title": "3D Avatar Builder Tutorial",
  "content_type": "youtube",
  "transcript": "Full transcript text...",
  "processed": true
}
```

### 2. Generate Gemini MCQs (NEW)
**POST** `/api/adaptive/content/{content_id}/generate_gemini_mcqs/`

**Request:**
```json
{
  "user_state": 4
}
```

**User States:**
- `1` = Confused → 20 simple/beginner questions
- `2` = Bored → 20 challenging/advanced questions
- `3` = Overloaded → 10 easy questions + break suggestion
- `4` = Focused → 20 intermediate-advanced questions (default)

**Response:**
```json
{
  "content_id": 1,
  "content_title": "3D Avatar Builder Tutorial",
  "user_state": "focused",
  "difficulty": "intermediate-to-advanced",
  "num_questions": 20,
  "take_break_suggestion": false,
  "questions": [
    {
      "question": "What is Three.js used for?",
      "options": {
        "A": "3D rendering in the browser",
        "B": "Backend API development",
        "C": "Database management",
        "D": "CSS styling"
      },
      "answer": "A",
      "explanation": "Three.js is a JavaScript library for 3D rendering in web browsers."
    }
  ]
}
```

## Frontend Integration

### Step 1: Upload YouTube Content
```javascript
import { contentAPI } from '../services/api';

// User pastes YouTube URL and clicks confirm
const handleUploadYouTube = async (url) => {
  const response = await contentAPI.upload({
    title: 'My Study Material',
    content_type: 'youtube',
    url: url
  });
  
  const contentId = response.data.id;
  // Store contentId for later use
};
```

### Step 2: Generate MCQs (Background)
```javascript
// After content is uploaded, generate MCQs in background
const generateMCQs = async (contentId, userState = 4) => {
  try {
    const response = await axios.post(
      `/api/adaptive/content/${contentId}/generate_gemini_mcqs/`,
      { user_state: userState }
    );
    
    // Store questions for assessment
    const questions = response.data.questions;
    return questions;
  } catch (error) {
    console.error('MCQ generation failed:', error);
  }
};
```

### Step 3: Show Assessment
```javascript
// When user clicks "Take Assessment"
const handleTakeAssessment = () => {
  // Display the generated questions
  navigate(`/assessment/${contentId}`, {
    state: { questions: generatedQuestions }
  });
};
```

## Complete Workflow Example

```javascript
// In your study session component
const [contentId, setContentId] = useState(null);
const [questions, setQuestions] = useState([]);
const [loading, setLoading] = useState(false);

// Step 1: User adds YouTube content
const handleAddYouTubeContent = async (url) => {
  setLoading(true);
  
  try {
    // Upload and process content
    const uploadResponse = await contentAPI.upload({
      title: 'Study Material',
      content_type: 'youtube',
      url: url
    });
    
    const newContentId = uploadResponse.data.id;
    setContentId(newContentId);
    
    // Generate MCQs in background
    const mcqResponse = await axios.post(
      `/api/adaptive/content/${newContentId}/generate_gemini_mcqs/`,
      { user_state: 4 } // focused
    );
    
    setQuestions(mcqResponse.data.questions);
    
    // Show success message
    alert('Content processed! MCQs ready for assessment.');
    
  } catch (error) {
    console.error('Error:', error);
    alert('Failed to process content');
  } finally {
    setLoading(false);
  }
};

// Step 2: User takes assessment
const handleTakeAssessment = () => {
  if (questions.length === 0) {
    alert('No questions available yet');
    return;
  }
  
  navigate(`/assessment`, {
    state: { questions, contentId }
  });
};
```

## Files Modified/Created

### New Files:
1. `learning/adaptive_learning/gemini_mcq_service.py` - Gemini integration service
2. `learning/test_gemini_mcq_generator.py` - Standalone test script
3. `learning/GEMINI_MCQ_INTEGRATION.md` - This documentation

### Modified Files:
1. `learning/learning/settings.py` - Added GEMINI_API_KEY
2. `learning/adaptive_learning/views.py` - Added generate_gemini_mcqs endpoint

## Testing

### Test the standalone script:
```bash
cd learning
python test_gemini_mcq_generator.py
```

### Test the API endpoint:
```bash
# 1. Upload YouTube content
curl -X POST http://localhost:8000/api/adaptive/content/upload/ \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","content_type":"youtube","url":"https://youtube.com/watch?v=..."}'

# 2. Generate MCQs (replace {content_id})
curl -X POST http://localhost:8000/api/adaptive/content/{content_id}/generate_gemini_mcqs/ \
  -H "Content-Type: application/json" \
  -d '{"user_state": 4}'
```

## Dependencies

Already installed:
- `youtube-transcript-api` - For fetching YouTube transcripts
- `google-generativeai` - For Gemini API (needs to be installed)

Install if missing:
```bash
pip install google-generativeai
```

## Configuration

The Gemini API key is stored in `settings.py`:
```python
GEMINI_API_KEY = 'AIzaSyAL99Z0RtQuCqKM_cvSay6yIVDsHGvDntc'
```

For production, use environment variables:
```python
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'default_key')
```

## Next Steps

1. **Frontend UI**: Create assessment page to display MCQs
2. **Answer Submission**: Add endpoint to submit answers and calculate score
3. **Progress Tracking**: Store assessment results in database
4. **User State Detection**: Automatically detect user state based on performance
5. **Caching**: Cache generated questions to avoid regenerating

## Notes

- MCQ generation takes 5-10 seconds depending on transcript length
- Questions are generated fresh each time (no caching yet)
- User state can be manually set or auto-detected from performance
- Break suggestions appear for overloaded users (state 3)
