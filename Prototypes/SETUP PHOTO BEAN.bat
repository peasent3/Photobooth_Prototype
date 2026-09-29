@echo off
setlocal
title PhotoBean Setup

cd /d "%~dp0"

echo ==========================================
echo          PHOTO BEAN SETUP
echo ==========================================
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python was not found in PATH.
    echo Install Python and make sure "Add Python to PATH" is enabled.
    pause
    exit /b 1
)

if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 goto :error
) else (
    echo Virtual environment already exists.
)

echo.
echo Upgrading pip...
"venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :error

echo.
echo Installing PhotoBean packages...
"venv\Scripts\python.exe" -m pip install Flask Pillow Werkzeug libusb1 qrcode boto3
if errorlevel 1 goto :error

echo.
echo Creating PhotoBean photo folders...
if not exist "C:\Photobooth" mkdir "C:\Photobooth"
if not exist "C:\Photobooth\Photos" mkdir "C:\Photobooth\Photos"
if not exist "C:\Photobooth\Photos\Designs" mkdir "C:\Photobooth\Photos\Designs"

echo.
echo ==========================================
echo PhotoBean setup completed successfully!
echo ==========================================
echo.
echo IMPORTANT:
echo - Install/configure the Sony camera WinUSB driver with Zadig.
echo - Configure the Sony A7C II for PC Remote.
echo - Make sure the Canon SELPHY CP1500 is installed in Windows.
echo.
echo You can now run LAUNCH PHOTO BEAN.bat
echo.
pause
exit /b 0

:error
echo.
echo ==========================================
echo SETUP FAILED
echo ==========================================
echo Check the error shown above.
pause
exit /b 1
