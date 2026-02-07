@echo off
title Invoice Project Launcher

echo ==================================================
echo       Smart Invoice Categorizer Launcher
echo ==================================================
echo.

:: Check for Python
python --version >NUL 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH!
    echo Please install Python and try again.
    pause
    exit /b
)

echo [Step 1] Installation Check
set /p install_deps="Do you want to check/install dependencies? (Y/N): "
if /i "%install_deps%"=="Y" (
    echo Installing requirements...
    pip install -r requirements.txt
    echo.
)

echo.
echo [Step 2] Starting Backend API...
start "Backend API" cmd /k "python src/api.py"

echo.
echo [Step 3] Starting Frontend Server...
cd frontend
start "Frontend Server" cmd /k "python -m http.server 8000"

echo.
echo [Step 4] Launching Browser...
timeout /t 4 > NUL
start http://localhost:8000

echo.
echo ==================================================
echo              PROJECT IS RUNNING
echo ==================================================
echo IMPORTANT:
echo 1. Keep the two new black terminal windows OPEN.
echo 2. If the browser didn't open, go to: http://localhost:8000
echo.
pause
