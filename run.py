#!/usr/bin/env python3
"""
Universal runner for Vision Tracker
Works on Windows, Linux, and WSL
"""

import os
import sys
import platform
import subprocess

def detect_platform():
    system = platform.system()
    is_wsl = 'microsoft' in platform.uname().release.lower()
    return {
        'system': system,
        'is_wsl': is_wsl,
        'is_windows': system == 'Windows',
        'is_linux': system == 'Linux' and not is_wsl,
        'platform_name': 'WSL' if is_wsl else system
    }

def check_dependencies():
    """Check if required Python packages are installed"""
    required = ['cv2', 'numpy', 'torch', 'ultralytics']
    missing = []
    
    for module in required:
        try:
            __import__(module)
        except ImportError:
            missing.append(module if module != 'cv2' else 'opencv-python')
    
    return missing

def install_dependencies():
    """Install missing dependencies"""
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    
    # Install PyTorch with appropriate backend
    platform_info = detect_platform()
    if platform_info['is_windows']:
        # Windows: CPU version (CUDA can be added if needed)
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', 
            'torch', 'torchvision', '--index-url', 
            'https://download.pytorch.org/whl/cpu'
        ])
    else:
        # Linux/WSL: CPU version
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', 
            'torch', 'torchvision', '--index-url', 
            'https://download.pytorch.org/whl/cpu'
        ])

def main():
    platform_info = detect_platform()
    
    print("=" * 50)
    print("Vision Tracker - Universal Runner")
    print("=" * 50)
    print(f"Platform: {platform_info['platform_name']}")
    print()
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        response = input("Install missing packages? (y/n): ")
        if response.lower() == 'y':
            install_dependencies()
        else:
            print("Cannot run without required packages.")
            sys.exit(1)
    
    # Platform-specific instructions
    if platform_info['is_wsl']:
        print("WSL Instructions:")
        print("1. For camera access, you need USB passthrough")
        print("2. Run ./setup-wsl-camera.sh for setup instructions")
        print("3. Or continue in test mode without camera")
        print()
    elif platform_info['is_windows']:
        print("Windows: Camera should work automatically")
        print("If not, check if camera is being used by another app")
        print()
    else:
        print("Linux: Camera should work if /dev/video0 exists")
        print("Run: ls /dev/video* to check available cameras")
        print()
    
    # Run the vision tracker
    print("Starting Vision Tracker...")
    print("Press 'q' in the window to quit")
    print("-" * 50)
    
    try:
        from vision_tracker import VisionTracker
        tracker = VisionTracker()
        tracker.run()
    except Exception as e:
        print(f"Error: {e}")
        if platform_info['is_wsl']:
            print("\nWSL Tip: Camera not accessible. Running in test mode is normal.")
        sys.exit(1)

if __name__ == "__main__":
    main()