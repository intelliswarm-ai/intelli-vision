#!/usr/bin/env python3
"""
Vision Tracker Lite - Minimal version without heavy dependencies
Works without YOLO model for testing purposes
"""

import sys
import time

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("OpenCV not available - running in text-only mode")

def run_text_mode():
    """Run in text-only mode when OpenCV is not available"""
    print("=" * 60)
    print("Vision Tracker Lite - Text Mode")
    print("=" * 60)
    print("\nSimulating vision tracking without GUI...")
    print("Press Ctrl+C to stop\n")
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            frame_count += 1
            elapsed = time.time() - start_time
            fps = frame_count / elapsed if elapsed > 0 else 0
            
            # Simulate detection
            detections = [
                f"Person (confidence: {0.85 + np.random.random()*0.1:.2f})",
                f"Car (confidence: {0.75 + np.random.random()*0.15:.2f})",
                f"Dog (confidence: {0.65 + np.random.random()*0.2:.2f})",
            ]
            
            # Clear line and print status
            print(f"\rFrame {frame_count:05d} | FPS: {fps:5.1f} | Detections: {', '.join(detections[:2])}", end="")
            
            time.sleep(0.033)  # ~30 FPS
            
    except KeyboardInterrupt:
        print(f"\n\nStopped. Processed {frame_count} frames in {elapsed:.1f} seconds")

def run_opencv_lite():
    """Run with OpenCV but without YOLO model"""
    print("=" * 60)
    print("Vision Tracker Lite - OpenCV Mode (No ML Model)")
    print("=" * 60)
    print("Running with basic motion detection")
    print("Controls:")
    print("  'q' - Quit")
    print("  'f' - Toggle fullscreen")
    print("  'r' - Reset window size")
    print("  SPACE - Pause/Resume\n")
    
    # Try to open camera or create test frames
    cap = cv2.VideoCapture(0)
    use_camera = cap.isOpened()
    
    if not use_camera:
        print("No camera found - using generated frames")
    
    # Create resizable window
    window_name = 'Vision Tracker Lite'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 800, 600)
    
    # For motion detection
    prev_frame = None
    frame_count = 0
    paused = False
    fullscreen = False
    
    while True:
        if not paused:
            if use_camera:
                ret, frame = cap.read()
                if not ret:
                    break
            else:
                # Generate test frame
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                t = time.time()
                
                # Moving circle
                cx = int(320 + 150 * np.sin(t))
                cy = int(240 + 100 * np.cos(t))
                cv2.circle(frame, (cx, cy), 30, (100, 200, 100), -1)
                
                # Add text
                cv2.putText(frame, "TEST MODE", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Simple motion detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        if prev_frame is not None:
            # Compute difference
            diff = cv2.absdiff(prev_frame, gray)
            thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Draw bounding boxes
            for contour in contours:
                if cv2.contourArea(contour) > 500:
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(frame, "Motion", (x, y-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        prev_frame = gray
        frame_count += 1
        
        # Add frame counter
        cv2.putText(frame, f"Frame: {frame_count}", (10, frame.shape[0]-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Show in resizable window
        cv2.imshow(window_name, frame)
        
        # Handle keyboard input
        key = cv2.waitKey(30) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('f'):
            fullscreen = not fullscreen
            if fullscreen:
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            else:
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
        elif key == ord('r'):
            cv2.resizeWindow(window_name, 800, 600)
        elif key == ord(' '):
            paused = not paused
    
    if use_camera:
        cap.release()
    cv2.destroyAllWindows()
    print(f"\nProcessed {frame_count} frames")

def main():
    print("\nVision Tracker Lite - Minimal Dependencies Version")
    print("This version works without YOLO model for testing\n")
    
    if OPENCV_AVAILABLE:
        try:
            run_opencv_lite()
        except Exception as e:
            print(f"OpenCV error: {e}")
            print("Falling back to text mode...")
            run_text_mode()
    else:
        run_text_mode()

if __name__ == "__main__":
    main()