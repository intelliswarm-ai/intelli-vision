@echo off
cls
echo ================================================
echo    Vision Tracker - Full YOLO Version
echo ================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

:: Quick dependency check
echo Checking dependencies...
python -c "import cv2, torch; from ultralytics import YOLO; print('✓ All dependencies OK')" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ⚠ Dependencies missing or incompatible!
    echo.
    set /p fix="Run dependency fix? (y/n) [default: y]: "
    if "%fix%"=="" set fix=y
    if /i "%fix%"=="y" (
        echo Running fix_yolo_dependencies.bat...
        call fix_yolo_dependencies.bat
        echo.
        echo Continuing with Vision Tracker...
    ) else (
        echo Continuing anyway... (may fail)
    )
)

echo.
echo Select mode:
echo   1. Auto-detect (Camera if available, test mode fallback)
echo   2. Test mode (Synthetic data with YOLO detection)
echo   3. Video file mode
echo   4. Generate sample video first
echo   5. Simple test (no YOLO, just scaling test)
echo.
set /p mode="Enter choice (1-5) [default: 2]: "

if "%mode%"=="" set mode=2

echo.
echo ================================================

if "%mode%"=="1" (
    echo Starting Vision Tracker with camera auto-detection...
    echo Window will be resizable - try maximizing it!
    echo.
    python vision_tracker.py
) else if "%mode%"=="2" (
    echo Starting Vision Tracker in test mode with YOLO...
    echo Window will be resizable - try maximizing it!
    echo.
    python vision_tracker.py --test
) else if "%mode%"=="3" (
    set /p video="Enter video file path (or press Enter for sample): "
    if "%video%"=="" (
        if exist "sample_video.mp4" (
            echo Using existing sample_video.mp4...
            python vision_tracker.py --source sample_video.mp4
        ) else (
            echo No sample video found. Generating one first...
            python generate_sample_video.py --duration 30
            if exist "sample_video.mp4" (
                python vision_tracker.py --source sample_video.mp4
            ) else (
                echo Failed to generate sample video. Using test mode...
                python vision_tracker.py --test
            )
        )
    ) else (
        python vision_tracker.py --source "%video%"
    )
) else if "%mode%"=="4" (
    echo Generating sample video...
    python generate_sample_video.py --duration 60 --fps 30
    echo.
    echo Sample video created! Now starting tracker...
    python vision_tracker.py --source sample_video.mp4
) else if "%mode%"=="5" (
    echo Starting simple scaling test (no YOLO)...
    python vision_tracker_simple.py
) else (
    echo Invalid choice. Starting test mode...
    python vision_tracker.py --test
)

echo.
echo ================================================
echo Vision Tracker stopped.
echo.
echo Tips for next run:
echo   • Window should resize properly when maximized
echo   • Press 'f' for fullscreen mode
echo   • Press 's' to save screenshots
echo   • Press SPACE to pause/resume
echo ================================================
pause