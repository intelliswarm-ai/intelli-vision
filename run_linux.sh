#!/bin/bash

echo "Vision Tracker - Linux/WSL Runner"
echo "=================================="
echo ""

# Detect if running in WSL
if grep -q Microsoft /proc/version; then
    echo "Detected WSL environment"
    IS_WSL=true
else
    echo "Detected native Linux environment"
    IS_WSL=false
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed"
    echo "Please install: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Check camera availability
echo ""
echo "Checking camera devices..."
if [ -e /dev/video0 ]; then
    echo "Camera found at /dev/video0"
else
    echo "No camera found - will run in test mode"
    if [ "$IS_WSL" = true ]; then
        echo ""
        echo "For WSL camera setup, run: ./setup-wsl-camera.sh"
    fi
fi

# Run the vision tracker
echo ""
echo "Starting Vision Tracker..."
echo "Press Ctrl+C to stop"
echo ""
python3 vision_tracker.py