@echo off
cls
echo ==========================================
echo    Vision Tracker - Auto-Scaling Version
echo ==========================================
echo.
echo This version automatically scales video when window is resized.
echo.
echo Controls:
echo   q - Quit
echo   f - Toggle fullscreen
echo   r - Reset window size
echo   + - Zoom in (increase scale)
echo   - - Zoom out (decrease scale)
echo   s - Save screenshot
echo   SPACE - Pause/Resume
echo.
echo Starting in test mode...
echo.

python vision_tracker_scalable.py --test

if %errorlevel% neq 0 (
    echo.
    echo Error running the scalable tracker.
    echo Trying lite version...
    python vision_tracker_lite.py
)

pause