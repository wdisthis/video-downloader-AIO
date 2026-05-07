@echo off
setlocal
title Video Downloader AIO - Setup

echo ===========================================
echo    SETTING UP VIDEO DOWNLOADER AIO
echo ===========================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python and try again.
    pause
    exit /b
)

:: Create VENV if not exists
if not exist venv (
    echo [1/3] Creating Virtual Environment...
    python -m venv venv
) else (
    echo [1/3] Virtual Environment already exists.
)

:: Install requirements
echo [2/3] Installing Dependencies...
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r setup/requirements.txt

:: Create folders
echo [3/3] Preparing Directories...
if not exist downloads mkdir downloads
if not exist static mkdir static
if not exist templates mkdir templates

echo.
echo ===========================================
echo    SETUP COMPLETE!
echo    Run 'RUN_APP.bat' to start the program.
echo ===========================================
echo.
pause
