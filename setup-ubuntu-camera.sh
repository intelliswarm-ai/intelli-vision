#!/bin/bash

echo "Ubuntu Camera Setup Script for Vision Tracker"
echo "============================================="
echo ""

# Check if running on Ubuntu
if ! lsb_release -a 2>/dev/null | grep -q Ubuntu; then
    echo "Warning: This script is optimized for Ubuntu"
fi

echo "Step 1: Install camera utilities"
echo "---------------------------------"
sudo apt update
sudo apt install -y v4l-utils guvcview cheese

echo ""
echo "Step 2: Check camera devices"
echo "-----------------------------"
echo "Available video devices:"
ls -la /dev/video*

echo ""
echo "Camera information:"
v4l2-ctl --list-devices

echo ""
echo "Step 3: Add user to video group"
echo "--------------------------------"
sudo usermod -a -G video $USER
echo "User $USER added to video group"

echo ""
echo "Step 4: Test camera access"
echo "---------------------------"
echo "Testing camera with v4l2-ctl..."
v4l2-ctl --device=/dev/video0 --all | head -20

echo ""
echo "Step 5: Set permissions for Docker"
echo "-----------------------------------"
# Ensure camera device has proper permissions
sudo chmod 666 /dev/video*

echo ""
echo "Step 6: Configure X11 for GUI display"
echo "--------------------------------------"
xhost +local:docker 2>/dev/null || echo "xhost not available, GUI may not work"

echo ""
echo "Setup complete!"
echo ""
echo "To test your camera:"
echo "  1. Native test: cheese (GUI camera app)"
echo "  2. Docker test: docker-compose up"
echo ""
echo "If you still have issues:"
echo "  - Make sure no other application is using the camera"
echo "  - Try: sudo docker-compose up (for permission issues)"
echo "  - Logout and login again for group changes to take effect"