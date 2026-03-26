@echo off
TITLE Smart Invoice Project Launcher

echo ======================================================
echo       Smart Invoice Project - Auto Launcher
echo ======================================================
echo.

python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python from https://www.python.org/
    echo.
    pause
    exit /b 1
)

echo [OK] Python is installed.
python --version
echo.

if exist requirements.txt (
    echo [INFO] Checking and installing dependencies...
    pip install -r requirements.txt
    IF %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
    echo [OK] Dependencies are ready.
) else (
    echo [WARNING] requirements.txt not found. Skipping dependency check.
)

echo.
echo ======================================================
echo       Starting Server...
echo ======================================================
echo.

python server.py

echo.
echo Server has stopped.
pause
