# Quick Start Guide - Adaptive Learning System

## 🚀 Get Running in 5 Minutes

### Step 1: Install Backend Dependencies (2 min)
```bash
cd learning
pip install -r requirements.txt
pip install -r adaptive_learning_requirements.txt
```

### Step 2: Setup Database (2 min)
```bash
# Train ML model
python adaptive_learning/train_model.py

# Run migrations
python manage.py makemigrations adaptive_learning
python manage.py migrate

# Create admin user
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: admin123
```

### Step 3: Start Backend (30 sec)
```bash
python manage.py runserver
```
✅ Backend running at http://localhost:8000

### Step 4: Start Frontend (30 sec)
```bash
# New terminal
cd frontend
npm install  # First time only
npm run dev
```
✅ Frontend running at http://localhost:5173

## 🧪 Test the API

### Option 1: Browser
1. Go to http://localhost:8000/admin
2. Login with admin credentials
3. Go to http://localhost:8000/api/adaptive/topics/
4. You should see an empty list: `{"count":0,"results":[]}`

### Option 2: Test Script
```bash
python test_adaptive_api.py
```

### Option 3: Postman/curl
```bash
# Get topics
curl http://localhost:8000/api/adaptive/topics/

# Create topic (after logging in)
curl -X POST http://localhost:8000/api/adaptive/topics/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Python Programming","description":"Learn Python"}'
```

## 📝 Quick API Reference

### Base URL
```
http://localhost:8000/api/adaptive
```

### Key Endpoints
```
GET    /topics/                     - List topics
POST   /topics/                     - Create topic
POST   /content/upload/             - Upload content
POST   /content/{id}/generate_assessment/  - Generate quiz
GET    /assessments/{id}/questions/ - Get questions
POST   /assessments/{id}/submit_answer/    - Submit answer
POST   /assessments/{id}/complete/  - Get results
```

## 🎯 Test User Flow

### 1. Create Topic
```javascript
// In React component
import { topicsAPI } from './services/api';

const topic = await topicsAPI.create({
  name: "Python Programming",
  description: "Learn Python basics"
});
```

### 2. Upload Content
```javascript
import { uploadContent } from './services/api';

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

### 4. Get Questions
```javascript
const questions = await assessmentAPI.getQuestions(assessmentId);
```

### 5. Submit Answers
```javascript
await assessmentAPI.submitAnswer(assessmentId, {
  question_id: questionId,
  selected_answer_index: 1,
  time_taken_seconds: 30
});
```

### 6. Get Results
```javascript
const results = await assessmentAPI.complete(assessmentId);
// Returns: score, adaptive_score, weak_concepts, next_difficulty
```

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt -r adaptive_learning_requirements.txt

# Check for errors
python manage.py check
```

### Frontend won't start
```bash
# Check Node version
node --version  # Should be 16+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### CORS errors
- Make sure Django server is running on port 8000
- Check `CORS_ALLOWED_ORIGINS` in settings.py includes `http://localhost:5173`

### Authentication errors
- Login via Django admin first: http://localhost:8000/admin
- Or temporarily disable authentication in views.py

### ML model not found
```bash
python adaptive_learning/train_model.py
```

## 📚 Documentation

- `SETUP_INSTRUCTIONS.md` - Detailed setup guide
- `README_ADAPTIVE_LEARNING.md` - Complete documentation
- `IMPLEMENTATION_SUMMARY.md` - What was built
- `ADAPTIVE_LEARNING_INTEGRATION_STATUS.md` - Current status

## 🎓 Next Steps

1. ✅ Backend is running
2. ✅ Frontend is running
3. ⏳ Update React components to use API
4. ⏳ Test end-to-end user flow
5. ⏳ Deploy for hackathon

## 💡 Pro Tips

- Use Django admin to inspect database: http://localhost:8000/admin
- Check API responses in browser DevTools Network tab
- Use React DevTools to debug component state
- Monitor Django console for backend errors
- Check browser console for frontend errors

## 🆘 Need Help?

1. Check the error message carefully
2. Review the documentation files
3. Test API endpoints individually
4. Check Django and React console logs
5. Verify all dependencies are installed

## ✨ You're Ready!

The backend is complete and working. Just connect your React components to the API and you're done!

Good luck! 🚀
