@echo off
echo ========================================
echo    Fixing YOLO Dependencies
echo ========================================
echo.
echo This will fix the pyparsing compatibility issue
echo and get YOLO working again.
echo.
pause

echo Step 1: Fixing pyparsing version...
pip uninstall -y pyparsing
pip install "pyparsing>=2.4.0,<4.0.0"

echo.
echo Step 2: Updating matplotlib (often causes issues)...
pip uninstall -y matplotlib
pip install "matplotlib>=3.5.0,<3.8.0"

echo.
echo Step 3: Ensuring compatible versions...
pip install --upgrade "numpy>=1.21.0,<2.0.0"

echo.
echo Step 4: Testing YOLO import...
python -c "
try:
    print('Testing imports...')
    import cv2
    print('✓ OpenCV OK')
    import numpy as np
    print('✓ NumPy OK')
    import torch
    print('✓ PyTorch OK')
    from ultralytics import YOLO
    print('✓ YOLO OK')
    print('')
    print('All imports successful! YOLO is ready.')
    
    # Quick YOLO test
    print('Testing YOLO model loading...')
    model = YOLO('yolov8n.pt')  # This will download if not present
    print('✓ YOLO model loaded successfully')
    
except ImportError as e:
    print(f'✗ Import error: {e}')
    print('Please run this script again or check the error above.')
    exit(1)
except Exception as e:
    print(f'✗ Error: {e}')
    exit(1)
"

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo    Success! YOLO is ready to use.
    echo ========================================
    echo.
    echo You can now run:
    echo   python vision_tracker.py --test
    echo   python vision_tracker.py  (for camera)
    echo.
) else (
    echo.
    echo ========================================
    echo    There were some issues.
    echo ========================================
    echo Please check the error messages above.
)

pause