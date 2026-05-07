@echo off
setlocal
title Video Downloader AIO - Server

echo ===========================================
echo    STARTING VIDEO DOWNLOADER AIO
echo ===========================================
echo.

if not exist venv (
    echo [ERROR] Virtual Environment not found.
    echo Please run 'SETUP.bat' first!
    echo.
    pause
    exit /b
)

echo Starting Flask server...
echo Press Ctrl+C to stop.
echo.

:: Run app using venv python
venv\Scripts\python.exe app.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application crashed or stopped unexpectedly.
    pause
)

endlocal
