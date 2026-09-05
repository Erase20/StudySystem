@echo off
chcp 65001 >nul
echo ==========================================
echo       Study System - Frontend Only
echo ==========================================
echo.

echo [1/1] Starting frontend service (port 8080)...
start "Frontend" cmd /k "cd /d %~dp0vue && npm run serve"

echo.
echo ==========================================
echo  Frontend started! 
echo  Access: http://localhost:8080
echo ==========================================
echo  Note: Make sure backend is already running on port 9090
echo ==========================================
pause
