@echo off
echo ========================================
echo    Fixing NumPy Compatibility Issue
echo ========================================
echo.
echo This will downgrade NumPy to a compatible version
echo and reinstall OpenCV to fix the import error.
echo.
pause

echo.
echo Step 1: Uninstalling current NumPy...
pip uninstall -y numpy

echo.
echo Step 2: Installing compatible NumPy (v1.24.3)...
pip install --no-cache-dir numpy==1.24.3

echo.
echo Step 3: Reinstalling OpenCV...
pip uninstall -y opencv-python opencv-python-headless opencv-contrib-python
pip install --no-cache-dir opencv-python==4.8.1.78

echo.
echo Step 4: Testing imports...
python -c "import cv2; import numpy as np; print(f'Success! NumPy {np.__version__}, OpenCV {cv2.__version__}')" 2>nul

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo    Fix completed successfully!
    echo ========================================
    echo.
    echo You can now run: python vision_tracker.py --test
) else (
    echo.
    echo ========================================
    echo    Some issues remain
    echo ========================================
    echo Please check the error messages above.
)

pause