#!/bin/bash

echo "================================================"
echo "Setting up WSL Display for Vision Tracker"
echo "================================================"

# Check if we're in WSL
if grep -qi microsoft /proc/version; then
    echo "✓ WSL detected"
    
    # Check WSL version
    if grep -qi "WSL2" /proc/version; then
        echo "✓ WSL2 detected - using WSLg display"
        export DISPLAY=:0
    else
        echo "✓ WSL1 detected - may need X11 server"
        export DISPLAY=localhost:0.0
    fi
    
    # Set environment variables for OpenCV
    export QT_X11_NO_MITSHM=1
    export LIBGL_ALWAYS_INDIRECT=1
    
    echo "Environment variables set:"
    echo "  DISPLAY=$DISPLAY"
    echo "  QT_X11_NO_MITSHM=$QT_X11_NO_MITSHM"
    echo "  LIBGL_ALWAYS_INDIRECT=$LIBGL_ALWAYS_INDIRECT"
    
else
    echo "Not running in WSL"
fi

echo ""
echo "Testing display connection..."

# Test X11 connection
if command -v xdpyinfo >/dev/null 2>&1; then
    if xdpyinfo >/dev/null 2>&1; then
        echo "✓ X11 display connection working"
    else
        echo "✗ X11 display connection failed"
        echo ""
        echo "Troubleshooting steps:"
        echo "1. Make sure you have WSLg enabled (Windows 11) or X11 server running"
        echo "2. Try: export DISPLAY=:0"
        echo "3. For older WSL: install VcXsrv or Xming on Windows"
    fi
else
    echo "Installing x11-utils for display testing..."
    sudo apt-get update && sudo apt-get install -y x11-utils
fi

echo ""
echo "Installing OpenCV without Qt dependencies..."
pip uninstall -y opencv-python opencv-contrib-python opencv-python-headless
pip install opencv-python-headless

echo ""
echo "================================================"
echo "Setup complete! Now try:"
echo "  python vision_tracker_headless.py"
echo "================================================"