@echo off
echo ========================================
echo Starting Frontend Server (Vite)
echo ========================================
echo.

REM Navigate to frontend directory
cd frontend

REM Check if node_modules exists
if not exist "node_modules\" (
    echo Installing dependencies...
    call npm install
    echo.
)

REM Start Vite dev server
echo Starting Vite development server...
echo Server will be available at: http://localhost:5173
echo Press CTRL+C to stop the server
echo.
call npm run dev
