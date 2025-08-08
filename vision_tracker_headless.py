#!/usr/bin/env python3
"""
Headless Vision Tracker - Works in WSL and headless environments
Saves frames to files instead of displaying them
"""

import cv2
import numpy as np
import time
import os
import sys

def generate_test_frame(frame_number=0):
    """Generate a test frame with clear scaling indicators"""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Add colorful background
    for i in range(480):
        for j in range(640):
            frame[i, j] = [
                int(128 + 127 * np.sin(i * 0.02 + frame_number * 0.1)),
                int(128 + 127 * np.sin(j * 0.02 + frame_number * 0.05)), 
                int(128 + 127 * np.sin((i + j) * 0.01 + frame_number * 0.08))
            ]
    
    # Add moving elements
    t = frame_number * 0.1
    
    # Moving circle
    cx = int(320 + 200 * np.sin(t * 0.5))
    cy = int(240 + 100 * np.cos(t * 0.7))
    cv2.circle(frame, (cx, cy), 40, (255, 255, 255), 3)
    cv2.circle(frame, (cx, cy), 35, (0, 255, 0), -1)
    
    # Corner markers with frame info
    corner_size = 50
    corners = [(0, 0), (640-corner_size, 0), (0, 480-corner_size), (640-corner_size, 480-corner_size)]
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
    
    for (x, y), color in zip(corners, colors):
        cv2.rectangle(frame, (x, y), (x + corner_size, y + corner_size), color, -1)
        cv2.putText(frame, f"F{frame_number}", (x + 5, y + 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
    
    # Grid lines
    grid_spacing = 80
    for x in range(0, 640, grid_spacing):
        cv2.line(frame, (x, 0), (x, 480), (100, 100, 100), 1)
    for y in range(0, 480, grid_spacing):
        cv2.line(frame, (0, y), (640, y), (100, 100, 100), 1)
    
    # Title and info
    cv2.putText(frame, f"HEADLESS MODE - Frame {frame_number}", (120, 50),
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, "Original Size: 640x480", (220, 100),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    cv2.putText(frame, f"Time: {time.strftime('%H:%M:%S')}", (220, 130),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    return frame

def test_opencv_backends():
    """Test which OpenCV backends are available"""
    print("Testing OpenCV backends...")
    
    backends = [
        ('NONE', cv2.CAP_ANY),
        ('V4L2', cv2.CAP_V4L2),
        ('GSTREAMER', cv2.CAP_GSTREAMER),
        ('FFMPEG', cv2.CAP_FFMPEG),
    ]
    
    available_backends = []
    for name, backend in backends:
        try:
            cap = cv2.VideoCapture(0, backend)
            if cap.isOpened():
                available_backends.append(name)
                cap.release()
                print(f"✓ {name} backend available")
            else:
                print(f"✗ {name} backend not available")
        except:
            print(f"✗ {name} backend failed")
    
    return available_backends

def main():
    print("=" * 60)
    print("Headless Vision Tracker - WSL Compatible")
    print("=" * 60)
    
    # Check environment
    if os.path.exists('/proc/version'):
        with open('/proc/version', 'r') as f:
            version_info = f.read()
            if 'microsoft' in version_info.lower():
                print("✓ Running in WSL")
                if 'WSL2' in version_info:
                    print("✓ WSL2 detected")
                else:
                    print("✓ WSL1 detected")
    
    print(f"✓ OpenCV version: {cv2.__version__}")
    print(f"✓ Python version: {sys.version}")
    
    # Test if we can create a window (will fail in headless)
    can_display = False
    try:
        test_window = "test"
        cv2.namedWindow(test_window, cv2.WINDOW_NORMAL)
        cv2.destroyWindow(test_window)
        can_display = True
        print("✓ GUI display available")
    except:
        print("✗ GUI display not available - running in headless mode")
    
    if can_display:
        print("\nTesting GUI mode...")
        run_gui_mode()
    else:
        print("\nRunning headless mode...")
        run_headless_mode()

def run_gui_mode():
    """Run with GUI display"""
    print("Starting GUI mode with resizable window...")
    
    window_name = "Vision Tracker - Scaling Test"
    
    try:
        # Create window with scaling flags
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
        cv2.resizeWindow(window_name, 800, 600)
        
        frame_count = 0
        
        while True:
            frame = generate_test_frame(frame_count)
            cv2.imshow(window_name, frame)
            
            key = cv2.waitKey(33) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                filename = f"frame_{frame_count:04d}.jpg"
                cv2.imwrite(filename, frame)
                print(f"Saved {filename}")
            
            frame_count += 1
            
            if frame_count >= 300:  # Auto-stop after 10 seconds
                break
        
        cv2.destroyAllWindows()
        
    except Exception as e:
        print(f"GUI mode failed: {e}")
        print("Falling back to headless mode...")
        run_headless_mode()

def run_headless_mode():
    """Run without GUI, save frames to files"""
    print("Running in headless mode - saving frames to files...")
    
    # Create output directory
    output_dir = "output_frames"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Generate some test frames
    num_frames = 30
    print(f"Generating {num_frames} test frames...")
    
    for i in range(num_frames):
        frame = generate_test_frame(i)
        
        # Save frame
        filename = os.path.join(output_dir, f"frame_{i:03d}.jpg")
        cv2.imwrite(filename, frame)
        
        # Show progress
        if i % 10 == 0:
            print(f"Generated frame {i}/{num_frames}")
        
        time.sleep(0.1)  # Small delay
    
    print(f"\n✓ Generated {num_frames} frames in {output_dir}/")
    print("You can view these frames to see the test pattern.")
    
    # Create a scaled version to demonstrate scaling
    print("\nCreating scaled versions...")
    scales = [0.5, 1.5, 2.0]
    
    sample_frame = generate_test_frame(15)  # Use middle frame
    
    for scale in scales:
        new_width = int(640 * scale)
        new_height = int(480 * scale)
        
        scaled_frame = cv2.resize(sample_frame, (new_width, new_height), 
                                interpolation=cv2.INTER_LINEAR if scale > 1 else cv2.INTER_AREA)
        
        filename = os.path.join(output_dir, f"scaled_{scale}x.jpg")
        cv2.imwrite(filename, scaled_frame)
        print(f"Created scaled version: {filename} ({new_width}x{new_height})")
    
    print(f"\n{'='*60}")
    print("Headless test complete!")
    print(f"Check the {output_dir}/ directory for generated frames.")
    print("The scaled versions show how the image would look at different sizes.")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()