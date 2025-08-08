#!/bin/bash

echo "=================================================="
echo "Vision Tracker - Docker Container"
echo "=================================================="

# Check for video devices
VIDEO_DEVICES=$(ls /dev/video* 2>/dev/null)

if [ -z "$VIDEO_DEVICES" ]; then
    echo "No video devices found in container."
    echo "Starting in test mode with synthetic data..."
    echo ""
    echo "To use a real camera:"
    echo "  1. Connect camera to host system"
    echo "  2. Run with: docker-compose up (with proper device mounting)"
    echo "  3. Or use: docker run --device=/dev/video0 vision-tracker"
    echo "=================================================="
    
    # Check if we have a video file to use
    if [ -f "/app/sample_video.mp4" ]; then
        echo "Found sample video. You can also run with:"
        echo "  python vision_tracker.py --source /app/sample_video.mp4"
    fi
    
    # Start in test mode
    exec python vision_tracker.py --test
else
    echo "Found video devices: $VIDEO_DEVICES"
    echo "Attempting to use camera..."
    echo "=================================================="
    
    # Try to use the first available video device
    exec python vision_tracker.py --source 0
fi