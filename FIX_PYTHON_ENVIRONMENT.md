# Fix Python Environment Issues

## Problem
You have mixed Python versions (3.10 and 3.13) and pandas doesn't support Python 3.13 yet.

## ✅ Quick Fix Applied

I've made the pandas import optional so the server will start. The recommendation system will fall back to popular courses if pandas is unavailable.

## 🔧 Permanent Solutions

### Option 1: Use Python 3.10 or 3.11 (RECOMMENDED)

```bash
# 1. Check available Python versions
py -0  # On Windows

# 2. Create new virtual environment with Python 3.10 or 3.11
py -3.10 -m venv venv
# OR
py -3.11 -m venv venv

# 3. Activate virtual environment
venv\Scripts\activate

# 4. Verify Python version
python --version  # Should show 3.10.x or 3.11.x

# 5. Install dependencies
cd learning
pip install --upgrade pip
pip install -r requirements.txt
pip install -r adaptive_learning_requirements.txt

# 6. Run migrations
python manage.py migrate

# 7. Start server
python manage.py runserver
```

### Option 2: Install Compatible Pandas for Python 3.13

```bash
# Try installing pandas from source (may take time)
pip install --no-binary pandas pandas

# OR wait for official pandas support for Python 3.13
```

### Option 3: Use Without Recommendations (Current State)

The server will now start without pandas. The recommendation system will:
- Fall back to showing popular courses
- All other features work normally
- Adaptive learning features are unaffected

## 🎯 What Changed

### 1. `learning/accounts/views.py`
```python
# Before
from courses.recommendations import get_recommendations_for_user

# After
try:
    from courses.recommendations import get_recommendations_for_user
except ImportError:
    def get_recommendations_for_user(user):
        return []
```

### 2. `learning/courses/recommendations.py`
```python
# Added at top
try:
    import pandas as pd
    import numpy as np
    from sklearn.neighbors import NearestNeighbors
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# Modified functions to check PANDAS_AVAILABLE
```

## 🚀 Try Starting Server Now

```bash
cd learning
python manage.py runserver
```

Should work now! The server will start and you can test the frontend integration.

## 📝 Notes

- **Adaptive learning features** (the main focus) don't require pandas
- **ML predictions** work fine without pandas
- **Only course recommendations** are affected
- All study session, monitoring, testing features work normally

## ✅ Verification

After server starts:
1. Check `http://localhost:8000/admin` - Should load
2. Check `http://localhost:8000/api/adaptive/` - Should show API root
3. Test creating topics and content
4. Test study sessions and tests

## 🔍 Check Your Python Environment

```bash
# Check which Python is being used
python --version
where python  # Windows
which python  # Linux/Mac

# Check installed packages
pip list | findstr pandas
pip list | findstr numpy
pip list | findstr scikit-learn
```

## 💡 Best Practice

For production, use Python 3.10 or 3.11 with a clean virtual environment:

```bash
# Clean setup
py -3.10 -m venv venv_clean
venv_clean\Scripts\activate
pip install --upgrade pip setuptools wheel
pip install -r learning/requirements.txt
pip install -r learning/adaptive_learning_requirements.txt
```

## 🆘 If Still Having Issues

1. **Delete old virtual environment**:
   ```bash
   deactivate
   rmdir /s venv  # Windows
   ```

2. **Create fresh environment with Python 3.10/3.11**

3. **Install dependencies fresh**

4. **Run migrations**

5. **Try again**

## 📞 Support

The server should now start successfully. All main features (adaptive learning, study sessions, monitoring, testing) work without pandas. Only the course recommendation system is affected.

