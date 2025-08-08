#!/bin/bash

echo "================================================"
echo "Fixing Vision Tracker Dependencies"
echo "================================================"

echo "Step 1: Fixing pyparsing compatibility issue..."
pip uninstall -y pyparsing
pip install 'pyparsing>=2.4.0,<4.0.0'

echo "Step 2: Testing imports..."
python -c "
try:
    import cv2
    print('✓ OpenCV import successful')
    import numpy as np
    print('✓ NumPy import successful')
    try:
        from ultralytics import YOLO
        print('✓ Ultralytics YOLO import successful')
    except ImportError as e:
        print(f'⚠ YOLO import failed: {e}')
        print('  This is OK - we have fallback versions')
except Exception as e:
    print(f'✗ Critical import failed: {e}')
    exit(1)
"

echo "================================================"
echo "Dependencies check complete!"
echo "================================================"
echo ""
echo "You can now run:"
echo "  python vision_tracker_simple.py    # Minimal version, no ML"
echo "  python vision_tracker_lite.py      # Basic motion detection"
echo "  python vision_tracker.py --test    # Full version with YOLO (if working)"
echo ""