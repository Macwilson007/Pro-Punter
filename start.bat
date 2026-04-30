@echo off
set "PATH=C:\Program Files\nodejs;%PATH%"
set "PATH=C:\Users\USER\AppData\Local\Programs\Python\Python314;%PATH%"
cd /d "%~dp0"

echo ========================================
echo     Pro Punter - Starting...
echo ========================================
echo.

echo [1/2] Starting Backend on port 8000...
start "Pro Punter Backend" cmd /k "cd /d %~dp0backend && py -m uvicorn app.main:app --reload --port 8000"

echo [2/2] Starting Frontend...
start "Pro Punter Frontend" cmd /k "cd /d %~dp0frontend && call npx next dev"

echo.
echo ========================================
echo     DONE! Opening browser...
echo ========================================
echo.

timeout /t 5 /nobreak >nul

start http://localhost:3000

echo Pro Punter is running!
echo Backend API: http://localhost:8000
echo Web App:     http://localhost:3000
echo.
echo Close this window to stop servers