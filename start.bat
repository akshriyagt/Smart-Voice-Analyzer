@echo off
echo ============================================
echo   Smart Voice Analyzer - Starting Server
echo ============================================

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.9+
    pause
    exit /b 1
)

:: Install dependencies if needed
echo Installing dependencies...
pip install -r requirements.txt -q

:: Start server
echo.
echo Starting server at http://localhost:8000
echo Press Ctrl+C to stop.
echo.
start "" "http://localhost:8000"
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

pause
