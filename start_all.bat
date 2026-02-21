@echo off
echo Starting Adaptive Learning Platform...
echo.

echo Starting Backend Server...
start "Backend Server" cmd /k "cd learning && python manage.py runserver"

timeout /t 3 /nobreak >nul

echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo.
echo Both servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press any key to exit this window (servers will keep running)
pause >nul
