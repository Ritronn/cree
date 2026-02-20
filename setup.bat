@echo off
REM Setup script for Eisenhower Matrix Task Management System (Windows)

echo === Eisenhower Matrix Task Management Setup ===
echo.

REM Check prerequisites
echo Checking prerequisites...

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed
    exit /b 1
)

where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Node.js is not installed
    exit /b 1
)

echo Prerequisites check passed!
echo.

REM Backend setup
echo === Setting up Backend ===
cd backend

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing Python dependencies...
pip install -r requirements.txt

echo Copying environment file...
if not exist .env (
    copy .env.example .env
    echo Created .env file. Please edit it with your configuration.
)

echo.
echo To complete backend setup, run:
echo   cd backend
echo   venv\Scripts\activate
echo   python manage.py makemigrations
echo   python manage.py migrate
echo   python manage.py createsuperuser
echo   python manage.py runserver
echo.

cd ..

REM Frontend setup
echo === Setting up Frontend ===
cd frontend

echo Installing Node dependencies...
call npm install

echo Copying environment file...
if not exist .env (
    copy .env.example .env
)

echo.
echo To start frontend, run:
echo   cd frontend
echo   npm run dev
echo.

cd ..

echo === Setup Complete ===
echo.
echo Next steps:
echo 1. Configure backend\.env with your database and API credentials
echo 2. Create PostgreSQL database: createdb eisenhower_matrix
echo 3. Run backend migrations (see commands above)
echo 4. Start backend server: cd backend ^&^& python manage.py runserver
echo 5. Start frontend server: cd frontend ^&^& npm run dev
echo 6. (Optional) Start Celery worker: cd backend ^&^& celery -A eisenhower_matrix worker -l info

pause
