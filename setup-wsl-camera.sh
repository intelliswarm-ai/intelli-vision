#!/bin/bash

echo "WSL Camera Setup Script"
echo "======================="
echo ""
echo "This script will help you set up camera access in WSL2 for Vision Tracker"
echo ""

# Check if running in WSL
if ! grep -q Microsoft /proc/version; then
    echo "Error: This script must be run in WSL2"
    exit 1
fi

echo "Step 1: Install USBIPD on Windows"
echo "-----------------------------------"
echo "1. Open PowerShell as Administrator on Windows (not WSL)"
echo "2. Run: winget install --interactive --exact dorssel.usbipd-win"
echo ""
echo "Press Enter when USBIPD is installed..."
read

echo ""
echo "Step 2: Install USB/IP tools in WSL"
echo "------------------------------------"
sudo apt update
sudo apt install -y linux-tools-generic hwdata
sudo update-alternatives --install /usr/local/bin/usbip usbip /usr/lib/linux-tools/*-generic/usbip 20

echo ""
echo "Step 3: List available USB devices"
echo "-----------------------------------"
echo "Run this in Windows PowerShell (as Administrator):"
echo "  usbipd list"
echo ""
echo "Find your camera device in the list (usually contains 'Camera' or 'Webcam')"
echo "Note the BUSID (e.g., 2-4)"
echo ""
echo "Enter your camera's BUSID: "
read BUSID

echo ""
echo "Step 4: Attach camera to WSL"
echo "-----------------------------"
echo "Run these commands in Windows PowerShell (as Administrator):"
echo "  usbipd bind --busid $BUSID"
echo "  usbipd attach --wsl --busid $BUSID"
echo ""
echo "Press Enter when camera is attached..."
read

echo ""
echo "Step 5: Verify camera in WSL"
echo "-----------------------------"
ls -la /dev/video* 2>/dev/null
if [ $? -eq 0 ]; then
    echo "Camera devices found!"
else
    echo "No camera devices found. Please check the attachment."
fi

echo ""
echo "Step 6: Test camera access"
echo "---------------------------"
echo "Installing v4l-utils for testing..."
sudo apt install -y v4l-utils

echo ""
echo "Camera information:"
v4l2-ctl --list-devices

echo ""
echo "Setup complete! You can now run the Vision Tracker."
echo ""
echo "To run Vision Tracker:"
echo "  docker-compose up"
echo ""
echo "Note: You may need to re-attach the camera after each Windows/WSL restart:"
echo "  In Windows PowerShell (Admin): usbipd attach --wsl --busid $BUSID"