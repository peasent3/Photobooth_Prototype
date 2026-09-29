@echo off
setlocal
title PhotoBean

cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo ==========================================
    echo PhotoBean virtual environment not found.
    echo ==========================================
    echo.
    echo Run SETUP PHOTO BEAN.bat first.
    echo.
    pause
    exit /b 1
)

if not exist "app.py" (
    echo ==========================================
    echo app.py was not found.
    echo ==========================================
    echo.
    echo Keep this BAT file inside the main Photobooth folder.
    echo.
    pause
    exit /b 1
)

echo ==========================================
echo          STARTING PHOTO BEAN
echo ==========================================
echo.
echo Main site:    http://localhost:5000
echo Design Studio: http://localhost:5000/design
echo.
echo Keep this window open while PhotoBean is running.
echo Press Ctrl+C to stop the server.
echo.

"venv\Scripts\python.exe" app.py

echo.
echo PhotoBean has stopped.
pause
