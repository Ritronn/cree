# Setup with Python 3.10 for ML Model

## Quick Setup Guide

### Step 1: Check Python 3.10 Installation

```bash
# Check if Python 3.10 is installed
py -3.10 --version

# Should show: Python 3.10.x
```

### Step 2: Create Virtual Environment with Python 3.10

```bash
# Navigate to project root
cd E:\Adaptive-Learning

# Create new virtual environment with Python 3.10
py -3.10 -m venv venv310

# Activate it
venv310\Scripts\activate

# Verify Python version
python --version
# Should show: Python 3.10.x
```

### Step 3: Install Dependencies

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install backend dependencies
cd learning
pip install -r requirements.txt
pip install -r adaptive_learning_requirements.txt

# This will install:
# - Django
# - djangorestframework
# - pandas (compatible with Python 3.10)
# - numpy
# - scikit-learn
# - joblib
# - All other dependencies
```

### Step 4: Verify ML Model Loads

```bash
# Still in learning directory
python manage.py check

# Should show:
# ✅ ML Model loaded from E:\Adaptive-Learning\learning\adaptive_learning\ml_models\random_forest_classifier_model.joblib
# System check identified no issues (0 silenced).
```

### Step 5: Run Migrations

```bash
python manage.py migrate
```

### Step 6: Start Server

```bash
python manage.py runserver

# Should start without warnings about ML model
```

## Verification

### Test ML Model is Working

```bash
# Open Django shell
python manage.py shell

# Test the ML predictor
from adaptive_learning.ml_predictor import predict_next_difficulty

user_data = {
    'accuracy': 90.0,
    'avg_time_per_question': 45.0,
    'first_attempt_correct': 85.0,
    'current_difficulty': 1,
    'sessions_completed': 5,
    'score_trend': 10.0,
    'mastery_level': 0.9,
    'is_new_topic': 0
}

result = predict_next_difficulty(user_data)
print(f"Next difficulty: {result}")
# Should return 2 (increased difficulty)

# Test with poor performance
user_data['accuracy'] = 40.0
user_data['current_difficulty'] = 2
result = predict_next_difficulty(user_data)
print(f"Next difficulty: {result}")
# Should return 1 (decreased difficulty)
```

## Frontend Setup

```bash
# Open new terminal
cd E:\Adaptive-Learning\frontend

# Install dependencies (only needed once)
npm install

# Start dev server
npm run dev
```

## Complete Workflow

### Terminal 1: Backend
```bash
cd E:\Adaptive-Learning
venv310\Scripts\activate
cd learning
python manage.py runserver
```

### Terminal 2: Frontend
```bash
cd E:\Adaptive-Learning\frontend
npm run dev
```

### Browser
```
http://localhost:5173
```

## Troubleshooting

### Issue: py -3.10 not found

**Solution**: Install Python 3.10 from python.org

```bash
# Download from: https://www.python.org/downloads/
# Install Python 3.10.x
# Make sure to check "Add Python to PATH"
```

### Issue: Virtual environment activation fails

**Solution**: Use full path

```bash
E:\Adaptive-Learning\venv310\Scripts\activate
```

### Issue: pip install fails

**Solution**: Upgrade pip and try again

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Issue: ML model still not loading

**Solution**: Check the model file exists

```bash
dir learning\adaptive_learning\ml_models\
# Should show: random_forest_classifier_model.joblib
```

If model file is missing, retrain it:

```bash
cd learning
python adaptive_learning/train_model.py
```

## Expected Output

When server starts with ML model loaded:

```
✅ ML Model loaded from E:\Adaptive-Learning\learning\adaptive_learning\ml_models\random_forest_classifier_model.joblib
Performing system checks...

System check identified no issues (0 silenced).
January 01, 2024 - 12:00:00
Django version 4.2.x, using settings 'learning.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

## Benefits of Using ML Model

With the trained ML model:
- ✅ More accurate difficulty predictions
- ✅ Learns from patterns in data
- ✅ Better personalization
- ✅ Smoother difficulty transitions
- ✅ Considers multiple factors simultaneously

## Next Steps

1. ✅ Set up Python 3.10 environment
2. ✅ Install dependencies
3. ✅ Verify ML model loads
4. ✅ Start both servers
5. ✅ Test complete workflow
6. ✅ Enjoy the full ML-powered adaptive learning!

## Quick Commands Reference

```bash
# Activate Python 3.10 environment
venv310\Scripts\activate

# Start backend
cd learning
python manage.py runserver

# Start frontend (new terminal)
cd frontend
npm run dev

# Test ML model (Django shell)
python manage.py shell
from adaptive_learning.ml_predictor import predict_next_difficulty
```

## Success Criteria

✅ Python 3.10 virtual environment created
✅ All dependencies installed
✅ ML model loads successfully
✅ Server starts without warnings
✅ Frontend connects to backend
✅ Complete workflow works

You're all set! 🚀
