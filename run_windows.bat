@echo off
echo Vision Tracker - Windows Runner
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install requirements
echo Installing requirements...
pip install --upgrade pip
pip install opencv-python==4.8.1.78
pip install ultralytics==8.0.196
pip install numpy==1.24.3
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

REM Run the vision tracker
echo.
echo Starting Vision Tracker...
echo Press Ctrl+C to stop
echo.
python vision_tracker.py

pause