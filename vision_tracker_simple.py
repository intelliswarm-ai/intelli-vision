#!/usr/bin/env python3
"""
Simple Vision Tracker - No Heavy Dependencies
Works without YOLO, focuses on proper window scaling
"""

import cv2
import numpy as np
import time
import sys

def generate_test_frame():
    """Generate a test frame with clear scaling indicators"""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Add colorful background
    for i in range(480):
        for j in range(640):
            frame[i, j] = [
                int(128 + 127 * np.sin(i * 0.02)),
                int(128 + 127 * np.sin(j * 0.02)), 
                int(128 + 127 * np.sin((i + j) * 0.01))
            ]
    
    # Add moving elements to see scaling in action
    t = time.time()
    
    # Moving circle
    cx = int(320 + 200 * np.sin(t * 0.5))
    cy = int(240 + 100 * np.cos(t * 0.7))
    cv2.circle(frame, (cx, cy), 40, (255, 255, 255), 3)
    cv2.circle(frame, (cx, cy), 35, (0, 255, 0), -1)
    
    # Corner markers to see scaling
    corner_size = 50
    corners = [(0, 0), (640-corner_size, 0), (0, 480-corner_size), (640-corner_size, 480-corner_size)]
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
    
    for (x, y), color in zip(corners, colors):
        cv2.rectangle(frame, (x, y), (x + corner_size, y + corner_size), color, -1)
        cv2.putText(frame, f"{x},{y}", (x + 5, y + 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
    
    # Grid lines to show scaling effect
    grid_spacing = 80
    for x in range(0, 640, grid_spacing):
        cv2.line(frame, (x, 0), (x, 480), (100, 100, 100), 1)
    for y in range(0, 480, grid_spacing):
        cv2.line(frame, (0, y), (640, y), (100, 100, 100), 1)
    
    # Title and instructions
    cv2.putText(frame, "SCALING TEST - Resize Window", (120, 50),
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, "Original Size: 640x480", (220, 100),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    cv2.putText(frame, "Press 'f' for fullscreen", (200, 400),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(frame, "Press 'q' to quit", (230, 430),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    return frame

def main():
    print("=" * 60)
    print("Simple Vision Tracker - Window Scaling Test")
    print("=" * 60)
    print("This will test if the window scales properly when resized.")
    print()
    print("Instructions:")
    print("1. The window will start at 640x480")
    print("2. Try resizing by dragging corners")
    print("3. Try maximizing the window")
    print("4. Press 'f' to toggle fullscreen")
    print("5. Press 'q' to quit")
    print("=" * 60)
    
    window_name = "Vision Tracker - Scaling Test"
    
    # Try different window creation methods for better compatibility
    try:
        # Method 1: Use all available flags for maximum compatibility
        flags = cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED
        cv2.namedWindow(window_name, flags)
        print("✓ Created window with full flags")
    except:
        try:
            # Method 2: Basic resizable window
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            print("✓ Created basic resizable window")
        except:
            # Method 3: Default window (not resizable)
            cv2.namedWindow(window_name)
            print("⚠ Created default window (may not be resizable)")
    
    # Set initial window size
    try:
        cv2.resizeWindow(window_name, 800, 600)
        print("✓ Set initial window size to 800x600")
    except:
        print("⚠ Could not set initial window size")
    
    frame_count = 0
    fullscreen = False
    
    print("\nWindow created. Starting video loop...")
    print("Watch the corner markers and grid to see if scaling works correctly.")
    
    while True:
        # Generate test frame
        frame = generate_test_frame()
        
        # Add frame counter
        cv2.putText(frame, f"Frame: {frame_count}", (10, 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Display frame
        cv2.imshow(window_name, frame)
        
        # Handle input
        key = cv2.waitKey(33) & 0xFF  # ~30 FPS
        
        if key == ord('q'):
            print("Quitting...")
            break
        elif key == ord('f'):
            fullscreen = not fullscreen
            if fullscreen:
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                print("Fullscreen ON")
            else:
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                print("Fullscreen OFF")
        elif key == ord('r'):
            cv2.resizeWindow(window_name, 800, 600)
            print("Reset window size")
        elif key == ord('i'):
            # Print current window info (if available)
            try:
                rect = cv2.getWindowImageRect(window_name)
                print(f"Window rect: {rect}")
            except:
                print("Cannot get window info")
        
        frame_count += 1
        
        # Simulate some delay
        time.sleep(0.01)
    
    cv2.destroyAllWindows()
    print(f"Processed {frame_count} frames")

if __name__ == "__main__":
    main()