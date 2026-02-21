# 🚀 START HERE - Complete Setup Guide

## Quick Start (3 Steps)

### Step 1: Setup Python 3.10 Environment

**Option A: Automated Setup (Recommended)**
```bash
# Double-click this file or run:
setup_python310.bat
```

**Option B: Manual Setup**
```bash
# Create virtual environment
py -3.10 -m venv venv310

# Activate it
venv310\Scripts\activate

# Install dependencies
cd learning
pip install -r requirements.txt
pip install -r adaptive_learning_requirements.txt

# Run migrations
python manage.py migrate
```

### Step 2: Start Backend Server

**Option A: Using Script**
```bash
# Double-click or run:
start_backend.bat
```

**Option B: Manual**
```bash
venv310\Scripts\activate
cd learning
python manage.py runserver
```

**Expected Output:**
```
✅ ML Model loaded from ...random_forest_classifier_model.joblib
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8000/
```

### Step 3: Start Frontend Server (New Terminal)

**Option A: Using Script**
```bash
# Double-click or run:
start_frontend.bat
```

**Option B: Manual**
```bash
cd frontend
npm install  # First time only
npm run dev
```

**Expected Output:**
```
VITE v5.x.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

## ✅ Verification

Open browser and navigate to: `http://localhost:5173`

You should see:
- ✅ Landing page loads
- ✅ Beautiful animations
- ✅ "Get Started Free" button
- ✅ No console errors

## 🎯 Test Complete Workflow

Follow this path to test everything:

1. **Landing Page** → Click "Get Started Free"
2. **Sign Up** → Fill form → Click "Create Account"
3. **Dashboard** → Click "Create Your First Topic"
4. **Create Topic** → Name: "Python" → Click "Create Topic"
5. **Topic Window** → Click "Add Content"
6. **Add Content** → Select "YouTube Video"
7. **YouTube URL** → Paste: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
8. **Watch Video** → Video should play
9. **Start Session** → Click "Take Assessment" (when implemented)
10. **Study Session** → Watch content, use whiteboard, chat
11. **Complete Session** → Click "Complete"
12. **Take Test** → Answer questions
13. **View Results** → See score and next difficulty
14. **Dashboard** → See updated progress

## 📁 Project Structure

```
E:\Adaptive-Learning\
├── learning/                    # Django Backend
│   ├── adaptive_learning/       # Main app
│   │   ├── ml_models/          # ML model files
│   │   ├── views.py            # API endpoints
│   │   └── models.py           # Database models
│   ├── manage.py               # Django management
│   └── requirements.txt        # Python dependencies
│
├── frontend/                    # React Frontend
│   ├── src/
│   │   ├── pages/              # All pages
│   │   ├── services/           # API integration
│   │   └── utils/              # Utilities
│   └── package.json            # Node dependencies
│
├── setup_python310.bat         # Setup script
├── start_backend.bat           # Start backend
├── start_frontend.bat          # Start frontend
└── START_HERE.md              # This file
```

## 🔧 Troubleshooting

### Python 3.10 Not Found

**Error:** `py -3.10 not found`

**Solution:**
1. Download Python 3.10 from https://www.python.org/downloads/
2. Install with "Add to PATH" checked
3. Restart terminal
4. Try again

### ML Model Not Loading

**Error:** `ML Model not found` or `couldn't be loaded`

**Solution:**
```bash
# Retrain the model
venv310\Scripts\activate
cd learning
python adaptive_learning/train_model.py
```

### Port Already in Use

**Error:** `Port 8000 is already in use`

**Solution:**
```bash
# Find and kill the process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use different port
python manage.py runserver 8001
```

### CORS Errors

**Error:** `CORS policy blocked`

**Solution:** Check `learning/learning/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
```

### Frontend Won't Start

**Error:** `npm: command not found`

**Solution:**
1. Install Node.js from https://nodejs.org/
2. Restart terminal
3. Try again

## 📚 Documentation

- **SETUP_PYTHON_3.10.md** - Detailed Python 3.10 setup
- **INTEGRATION_SUMMARY.md** - Complete integration overview
- **QUICK_TEST_WORKFLOW.md** - Step-by-step testing guide
- **FRONTEND_BACKEND_INTEGRATION_COMPLETE.md** - API documentation
- **ML_MODEL_INFO.md** - ML model information

## 🎓 Features

### Backend (Django)
- ✅ 30+ REST API endpoints
- ✅ ML-based adaptive difficulty
- ✅ Study session monitoring
- ✅ Proctoring system
- ✅ Test generation
- ✅ Progress tracking
- ✅ Chat integration

### Frontend (React)
- ✅ 8 complete pages
- ✅ Responsive design
- ✅ Smooth animations
- ✅ Real-time monitoring
- ✅ Interactive whiteboard
- ✅ AI chat assistant

## 🔑 Key URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | Main application |
| Backend API | http://localhost:8000/api/adaptive/ | REST API |
| Django Admin | http://localhost:8000/admin | Admin panel |
| API Docs | http://localhost:8000/api/ | API root |

## 🧪 Testing

### Quick API Test
```bash
# Test topics endpoint
curl http://localhost:8000/api/adaptive/topics/

# Create a topic
curl -X POST http://localhost:8000/api/adaptive/topics/ \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"Test Topic\", \"description\": \"Testing\"}"
```

### Automated Testing
```bash
# Test all backend APIs
python test_backend_apis.py

# Run Django tests
cd learning
python manage.py test adaptive_learning
```

## 💡 Tips

1. **Always use Python 3.10 environment** for ML model support
2. **Keep both servers running** while testing
3. **Check browser console** for frontend errors
4. **Check Django logs** for backend errors
5. **Use Django admin** to inspect database

## 🎯 Success Checklist

- [ ] Python 3.10 environment created
- [ ] All dependencies installed
- [ ] ML model loads successfully
- [ ] Backend server starts
- [ ] Frontend server starts
- [ ] Landing page loads
- [ ] Can create topics
- [ ] Can upload content
- [ ] Can start study sessions
- [ ] Can take tests
- [ ] Progress tracks correctly

## 🆘 Need Help?

1. Check the troubleshooting section above
2. Review documentation files
3. Check browser console for errors
4. Check Django server logs
5. Verify both servers are running

## 🎉 You're Ready!

Everything is set up and ready to go. Just run:

```bash
# Terminal 1
start_backend.bat

# Terminal 2
start_frontend.bat

# Browser
http://localhost:5173
```

**Happy Learning! 🚀**
