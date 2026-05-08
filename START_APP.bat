@echo off
setlocal
title Video Downloader AIO - Launcher

echo ===========================================
echo    STARTING VIDEO DOWNLOADER AIO
echo ===========================================
echo.

:: Try global python first as it's confirmed working by the user
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_EXE=python
) else if exist venv (
    set PYTHON_EXE=venv\Scripts\python.exe
) else (
    echo [ERROR] Python not found.
    pause
    exit /b
)

:: Open the web interface in the default browser
echo [1/2] Opening browser at http://localhost:5000...
start http://localhost:5000

:: Run the Flask application
echo [2/2] Launching server using: %PYTHON_EXE%
%PYTHON_EXE% app.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] The application crashed or failed to start.
    echo Please make sure all dependencies are installed.
    pause
)

endlocal
