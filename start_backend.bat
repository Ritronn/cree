@echo off
echo ========================================
echo Starting Backend Server (Python 3.10)
echo ========================================
echo.

REM Activate virtual environment
call venv310\Scripts\activate.bat

REM Navigate to learning directory
cd learning

REM Start Django server
echo Starting Django development server...
echo Server will be available at: http://localhost:8000
echo Press CTRL+C to stop the server
echo.
python manage.py runserver
