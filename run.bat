@echo off
SETLOCAL EnableDelayedExpansion
TITLE Smart Invoice Project Launcher
COLOR 0B

echo.
echo  ============================================================
echo       Smart Invoice Project - Auto Launcher
echo  ============================================================
echo.

REM ---------------------------------------------------------------
REM  1. CHECK PYTHON
REM ---------------------------------------------------------------
echo  [1/6] Checking Python installation...
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo  [ERROR] Python is NOT installed or not in your PATH.
    echo  Please install Python 3.10+ from https://www.python.org/
    echo  IMPORTANT: Check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)
FOR /F "tokens=*" %%i IN ('python --version 2^>^&1') DO SET PYVER=%%i
echo  [OK] %PYVER% detected.
echo.

REM ---------------------------------------------------------------
REM  2. CHECK PIP
REM ---------------------------------------------------------------
echo  [2/6] Checking pip...
python -m pip --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo  [WARN] pip not found. Attempting to install pip...
    python -m ensurepip --upgrade >nul 2>&1
    IF %ERRORLEVEL% NEQ 0 (
        echo  [ERROR] Failed to install pip. Please install it manually.
        pause
        exit /b 1
    )
)
echo  [OK] pip is available.
echo.

REM ---------------------------------------------------------------
REM  3. CHECK TESSERACT OCR
REM ---------------------------------------------------------------
echo  [3/6] Checking Tesseract OCR...

SET TESSERACT_FOUND=0

REM Check if tesseract is already in PATH
tesseract --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    SET TESSERACT_FOUND=1
    echo  [OK] Tesseract OCR found in PATH.
)

REM Check common install locations if not in PATH
IF !TESSERACT_FOUND! EQU 0 (
    IF EXIST "C:\Program Files\Tesseract-OCR\tesseract.exe" (
        SET "PATH=C:\Program Files\Tesseract-OCR;%PATH%"
        SET TESSERACT_FOUND=1
        echo  [OK] Tesseract OCR found at C:\Program Files\Tesseract-OCR
    )
)
IF !TESSERACT_FOUND! EQU 0 (
    IF EXIST "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe" (
        SET "PATH=C:\Program Files (x86)\Tesseract-OCR;%PATH%"
        SET TESSERACT_FOUND=1
        echo  [OK] Tesseract OCR found at C:\Program Files ^(x86^)\Tesseract-OCR
    )
)
IF !TESSERACT_FOUND! EQU 0 (
    IF EXIST "%LOCALAPPDATA%\Tesseract-OCR\tesseract.exe" (
        SET "PATH=%LOCALAPPDATA%\Tesseract-OCR;%PATH%"
        SET TESSERACT_FOUND=1
        echo  [OK] Tesseract OCR found at %LOCALAPPDATA%\Tesseract-OCR
    )
)

IF !TESSERACT_FOUND! EQU 0 (
    echo.
    echo  [ERROR] Tesseract OCR is NOT installed!
    echo.
    echo  Tesseract is required for invoice text extraction.
    echo  Please download and install it from:
    echo    https://github.com/UB-Mannheim/tesseract/wiki
    echo.
    echo  During installation:
    echo    - Use the default install path
    echo    - Check "Add to system PATH" if available
    echo.
    echo  After installing, run this script again.
    echo.
    pause
    exit /b 1
)
echo.

REM ---------------------------------------------------------------
REM  4. INSTALL PYTHON DEPENDENCIES
REM ---------------------------------------------------------------
echo  [4/6] Installing Python dependencies...
echo         (this may take a few minutes on first run)
echo.

IF NOT EXIST requirements.txt (
    echo  [ERROR] requirements.txt not found!
    echo  Please make sure you're running from the project folder.
    pause
    exit /b 1
)

python -m pip install -r requirements.txt --quiet --disable-pip-version-check 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo  [WARN] Some packages may have failed. Retrying with verbose output...
    python -m pip install -r requirements.txt --disable-pip-version-check
    IF %ERRORLEVEL% NEQ 0 (
        echo.
        echo  [ERROR] Failed to install dependencies.
        echo  Try running manually: pip install -r requirements.txt
        pause
        exit /b 1
    )
)
echo  [OK] All Python dependencies installed.
echo.

REM ---------------------------------------------------------------
REM  5. VERIFY CRITICAL IMPORTS & MODEL
REM ---------------------------------------------------------------
echo  [5/6] Verifying project setup...

python -c "import flask; import pandas; import pytesseract; import PIL; import sklearn; import tensorflow; print('IMPORTS_OK')" 2>nul | findstr "IMPORTS_OK" >nul
IF %ERRORLEVEL% NEQ 0 (
    echo  [ERROR] Critical Python packages failed to import.
    echo  Try deleting any __pycache__ folders and running again.
    echo.
    pause
    exit /b 1
)
echo  [OK] All critical packages verified.

REM Check if the NN model loads properly, retrain if needed
python -c "import tensorflow as tf; m = tf.keras.models.load_model('nn_model.keras'); print('MODEL_OK')" 2>nul | findstr "MODEL_OK" >nul
IF %ERRORLEVEL% NEQ 0 (
    echo  [WARN] Neural network model is incompatible with installed Keras version.
    echo         Retraining model... (this takes ~30 seconds)
    echo.
    IF EXIST "training_data\categories.csv" (
        python train_nn.py
        IF %ERRORLEVEL% NEQ 0 (
            echo  [WARN] Model retraining failed. Classification will use fallback mode.
        ) ELSE (
            echo  [OK] Model retrained successfully.
        )
    ) ELSE (
        echo  [WARN] Training data not found. Classification will use fallback mode.
    )
) ELSE (
    echo  [OK] Neural network model loaded successfully.
)
echo.

REM ---------------------------------------------------------------
REM  6. CREATE OUTPUT DIRECTORIES
REM ---------------------------------------------------------------
echo  [6/6] Preparing workspace...
IF NOT EXIST "invoices" mkdir "invoices"
IF NOT EXIST "output" mkdir "output"
IF NOT EXIST ".env" (
    echo LLM_API_KEY=> ".env"
    echo  [INFO] Created .env file. Add your Gemini API key for LLM features.
)
echo  [OK] Workspace ready.
echo.

REM ---------------------------------------------------------------
REM  LAUNCH SERVER
REM ---------------------------------------------------------------
echo  ============================================================
echo       All checks passed! Starting server...
echo  ============================================================
echo.
echo  The app will open in your browser at: http://localhost:5000
echo  Press Ctrl+C in this window to stop the server.
echo.

REM Open browser after a short delay (gives server time to start)
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:5000"

python server.py

echo.
echo  Server has stopped.
pause
