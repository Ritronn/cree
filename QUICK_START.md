# 🚀 Quick Start Guide - Adaptive Learning Features

## ✅ Verification

Run this to verify all files are in place:
```bash
python verify_integration.py
```

## 🏃 Start the Application

### 1. Start Backend (Terminal 1)
```bash
cd learning
python manage.py runserver
```

Backend will run on: `http://localhost:8000`

### 2. Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```

Frontend will run on: `http://localhost:5173`

## 🎯 Access New Features

1. **Open Browser**: Navigate to `http://localhost:5173`

2. **Login**: Use your credentials (or create an account)

3. **Go to Dashboard**: You'll see two new buttons in the header:
   - **Adaptive Suggestions** (Purple button with TrendingUp icon)
   - **Course Suggestions** (Blue button with Award icon)

## 📱 Feature Overview

### Adaptive Suggestions
**What it does**: Shows personalized learning resources for your weak areas

**How to use**:
1. Complete some tests (with some incorrect answers to create weak points)
2. Click "Adaptive Suggestions" in dashboard
3. View your weak points with accuracy metrics
4. Browse YouTube playlists, articles, and Q&A for each weak area
5. Click any suggestion to open it in a new tab
6. Use the refresh button to get new suggestions

### Course Suggestions
**What it does**: Recommends courses based on your study topics

**How to use**:
1. Study some topics in the system
2. Click "Course Suggestions" in dashboard
3. Switch between two tabs:
   - **Recent Topics**: YouTube playlists, articles, Q&A for topics you've studied
   - **Coursera Certificates**: Professional certificates from top universities

## 🔌 API Endpoints

All endpoints require authentication token in header:
```
Authorization: Token <your-token>
```

### Base URL
```
http://localhost:8000/api/adaptive/
```

### Endpoints

1. **Get Weak Point Suggestions**
   ```
   GET /adaptive-suggestions/weak_point_suggestions/
   ```

2. **Get Recent Topic Suggestions**
   ```
   GET /adaptive-suggestions/recent_topic_suggestions/
   ```

3. **Get Coursera Certificates**
   ```
   GET /adaptive-suggestions/coursera_certificates/
   ```

4. **Mark Suggestion as Viewed**
   ```
   POST /adaptive-suggestions/mark_suggestion_viewed/
   Body: { "suggestion_id": 1 }
   ```

5. **Refresh Suggestions**
   ```
   POST /adaptive-suggestions/refresh_suggestions/
   Body: { "weak_point_id": 1 }
   ```

## 🧪 Testing

### Create Test Data

1. **Create a user** (if you don't have one):
   - Go to signup page
   - Create account

2. **Create weak points**:
   - Complete some assessments
   - Answer some questions incorrectly
   - System will automatically identify weak areas

3. **Create topics**:
   - Study some content
   - System tracks your topics automatically

### Manual API Testing

Use tools like Postman or curl:

```bash
# Get weak point suggestions
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/adaptive/adaptive-suggestions/weak_point_suggestions/

# Get Coursera certificates
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/adaptive/adaptive-suggestions/coursera_certificates/
```

## 🎨 UI Features

### Adaptive Suggestions Page
- **Gradient Background**: Purple → Indigo → Blue
- **Glassmorphism Cards**: Frosted glass effect
- **Color-Coded Accuracy**:
  - 🔴 Red: < 50%
  - 🟡 Yellow: 50-70%
  - 🟢 Green: > 70%
- **Source Icons**: YouTube, Articles, Stack Overflow
- **Refresh Button**: Get new suggestions
- **View Tracking**: Marks suggestions as viewed

### Course Suggestions Page
- **Tab Navigation**: Switch between Recent Topics and Coursera
- **YouTube Playlists**: Real playlist links with channel info
- **Articles**: Current tutorials and guides
- **Q&A**: Stack Overflow questions with vote counts
- **Certificate Cards**: Professional certificates with:
  - Provider badges
  - Duration
  - Difficulty level
  - Direct links to Coursera

## 🔧 Troubleshooting

### Backend Issues

**Problem**: Django server won't start
```bash
# Solution: Check if port 8000 is in use
netstat -ano | findstr :8000
# Kill the process if needed
```

**Problem**: Module not found errors
```bash
# Solution: Install dependencies
cd learning
pip install -r requirements.txt
pip install -r adaptive_learning_requirements.txt
```

### Frontend Issues

**Problem**: React app won't start
```bash
# Solution: Install dependencies
cd frontend
npm install
```

**Problem**: API calls failing
- Check if backend is running on port 8000
- Check browser console for errors
- Verify authentication token is valid

### Feature Issues

**Problem**: No weak points showing
- Complete at least one test
- Answer some questions incorrectly
- Check if WeakPoint objects are created in database

**Problem**: No suggestions appearing
- Weak points need to be created first
- Try clicking the refresh button
- Check browser console for API errors

**Problem**: Scraper not working
- Web scraper requires Chrome browser
- Check internet connection
- Fallback data will be used if scraper fails

## 📊 Database Check

To verify data in database:

```bash
cd learning
python manage.py shell
```

```python
# Check weak points
from adaptive_learning.models import WeakPoint
WeakPoint.objects.all()

# Check recommendations
from adaptive_learning.models import CourseRecommendation
CourseRecommendation.objects.all()

# Check topics
from adaptive_learning.models import Topic
Topic.objects.all()
```

## 🎓 User Flow Example

1. **User completes a Python test**
   - Gets 4/10 questions on "For Loops" wrong
   - System creates WeakPoint: "Python Loops" (40% accuracy)

2. **User goes to Dashboard**
   - Sees "Adaptive Suggestions" button
   - Clicks it

3. **Adaptive Suggestions Page**
   - Shows "Python Loops" as weak point
   - Displays suggestions:
     - 5 YouTube playlists about Python loops
     - 5 articles/tutorials
     - 3 Stack Overflow questions
   - User clicks on a YouTube playlist
   - Opens in new tab
   - System marks as viewed

4. **User studies the content**
   - Watches videos
   - Reads articles
   - Practices

5. **User retakes test**
   - Gets 8/10 questions correct
   - Accuracy improves to 80%
   - Weak point removed or confidence score increases

## 📈 Success Metrics

Track these to measure feature success:
- Number of weak points identified
- Number of suggestions clicked
- Improvement in weak area accuracy
- Time spent on suggested resources
- Number of certificates explored
- User engagement rate

## 🎉 That's It!

You now have a fully functional adaptive learning system with:
- ✅ Real-time web scraping
- ✅ Personalized suggestions
- ✅ Professional certificate recommendations
- ✅ Beautiful, responsive UI
- ✅ Complete backend integration

**Enjoy learning! 🚀**

---

For detailed documentation, see:
- `ADAPTIVE_LEARNING_FEATURES.md` - Complete feature documentation
- `INTEGRATION_COMPLETE.md` - Integration summary

For issues, check the troubleshooting section above or review the documentation files.
