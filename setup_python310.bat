@echo off
echo ========================================
echo Setting up Python 3.10 Environment
echo ========================================
echo.

REM Check if Python 3.10 is available
py -3.10 --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.10 not found!
    echo Please install Python 3.10 from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Found Python 3.10
py -3.10 --version
echo.

REM Create virtual environment
echo Creating virtual environment with Python 3.10...
py -3.10 -m venv venv310
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo Virtual environment created successfully!
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv310\Scripts\activate.bat
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install backend dependencies
echo Installing backend dependencies...
cd learning
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements.txt
    pause
    exit /b 1
)

pip install -r adaptive_learning_requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install adaptive_learning_requirements.txt
    pause
    exit /b 1
)
echo.

REM Run migrations
echo Running database migrations...
python manage.py migrate
echo.

REM Check system
echo Checking Django system...
python manage.py check
echo.

cd ..

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the backend server:
echo   1. venv310\Scripts\activate
echo   2. cd learning
echo   3. python manage.py runserver
echo.
echo To start the frontend server (new terminal):
echo   1. cd frontend
echo   2. npm install (first time only)
echo   3. npm run dev
echo.
pause
