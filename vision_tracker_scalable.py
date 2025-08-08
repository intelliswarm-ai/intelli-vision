#!/usr/bin/env python3
"""
Vision Tracker with Automatic Window Scaling
Ensures video scales properly when window is resized or maximized
"""

import cv2
import numpy as np
import time
import argparse
import sys
import os

def detect_platform():
    """Detect the current platform"""
    import platform
    system = platform.system()
    return system == 'Windows'

class ScalableVisionTracker:
    def __init__(self, video_source=None, test_mode=False):
        self.video_source = video_source
        self.test_mode = test_mode
        self.cap = None
        self.window_name = 'Vision Tracker - Scalable Display'
        self.target_width = 1280  # Target display width
        self.target_height = 720  # Target display height
        
        # Initialize video capture
        if not test_mode and video_source is not None:
            self.cap = cv2.VideoCapture(video_source)
            if not self.cap.isOpened():
                print(f"Cannot open video source: {video_source}")
                print("Switching to test mode...")
                self.test_mode = True
                self.cap = None
        
        # Setup window with specific flags for better scaling
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)
        cv2.resizeWindow(self.window_name, self.target_width, self.target_height)
        
    def generate_test_frame(self):
        """Generate a test frame with moving elements"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Add gradient background
        for i in range(480):
            frame[i, :] = [20 + i//8, 30 + i//6, 40 + i//4]
        
        # Add moving elements
        t = time.time()
        
        # Moving circles
        for i in range(3):
            offset = i * 2.0
            cx = int(320 + 200 * np.sin(t * 0.5 + offset))
            cy = int(240 + 100 * np.cos(t * 0.7 + offset))
            color = (100 + i*50, 150 - i*30, 200 - i*40)
            cv2.circle(frame, (cx, cy), 30 + i*10, color, -1)
        
        # Moving rectangles
        for i in range(2):
            rx = int(100 + 400 * ((t * 0.3 + i) % 1))
            ry = 300 + i * 80
            color = (50 + i*100, 100, 200 - i*50)
            cv2.rectangle(frame, (rx, ry), (rx + 60, ry + 40), color, -1)
        
        # Add grid overlay for size reference
        grid_spacing = 80
        for x in range(0, 640, grid_spacing):
            cv2.line(frame, (x, 0), (x, 480), (50, 50, 50), 1)
        for y in range(0, 480, grid_spacing):
            cv2.line(frame, (0, y), (640, y), (50, 50, 50), 1)
        
        # Add text
        cv2.putText(frame, "TEST MODE - Scalable Display", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, f"Original: 640x480", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(frame, f"Time: {time.strftime('%H:%M:%S')}", (10, 460),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        return frame
    
    def resize_with_aspect_ratio(self, frame, width=None, height=None):
        """Resize frame maintaining aspect ratio"""
        h, w = frame.shape[:2]
        
        if width is None and height is None:
            return frame
        
        if width is None:
            # Calculate width based on height
            aspect_ratio = w / h
            width = int(height * aspect_ratio)
        elif height is None:
            # Calculate height based on width
            aspect_ratio = h / w
            height = int(width * aspect_ratio)
        else:
            # Fit within the given dimensions
            aspect_ratio = w / h
            if width / height > aspect_ratio:
                width = int(height * aspect_ratio)
            else:
                height = int(width / aspect_ratio)
        
        return cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)
    
    def run(self):
        print("=" * 60)
        print("Scalable Vision Tracker")
        print("=" * 60)
        print("Controls:")
        print("  'q' - Quit")
        print("  'f' - Toggle fullscreen")
        print("  'r' - Reset window size")
        print("  '+' - Increase display size")
        print("  '-' - Decrease display size")
        print("  's' - Save screenshot")
        print("  SPACE - Pause/Resume")
        print("=" * 60)
        
        frame_count = 0
        fps = 0
        fps_time = time.time()
        paused = False
        fullscreen = False
        scale_factor = 1.0
        
        while True:
            # Get frame
            if not paused:
                if self.test_mode:
                    frame = self.generate_test_frame()
                    time.sleep(0.033)  # Simulate 30 FPS
                else:
                    ret, frame = self.cap.read()
                    if not ret:
                        print("End of video or camera error")
                        break
                
                # Store original frame for processing
                original_frame = frame.copy()
                frame_count += 1
            
            # Calculate FPS
            if frame_count % 30 == 0:
                current_time = time.time()
                fps = 30 / (current_time - fps_time)
                fps_time = current_time
            
            # Add overlay information
            display_frame = original_frame.copy()
            cv2.putText(display_frame, f"FPS: {fps:.1f}", (10, display_frame.shape[0] - 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(display_frame, f"Scale: {scale_factor:.1f}x", (10, display_frame.shape[0] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            if paused:
                cv2.putText(display_frame, "PAUSED", 
                           (display_frame.shape[1]//2 - 60, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
            
            # Apply manual scaling
            if scale_factor != 1.0:
                new_width = int(display_frame.shape[1] * scale_factor)
                new_height = int(display_frame.shape[0] * scale_factor)
                display_frame = cv2.resize(display_frame, (new_width, new_height), 
                                          interpolation=cv2.INTER_LINEAR if scale_factor > 1 else cv2.INTER_AREA)
            
            # Display the frame
            cv2.imshow(self.window_name, display_frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('f'):
                fullscreen = not fullscreen
                if fullscreen:
                    cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                    print("Fullscreen ON")
                else:
                    cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                    print("Fullscreen OFF")
            elif key == ord('r'):
                scale_factor = 1.0
                cv2.resizeWindow(self.window_name, self.target_width, self.target_height)
                print("Window reset")
            elif key == ord('+') or key == ord('='):
                scale_factor = min(scale_factor + 0.1, 3.0)
                print(f"Scale: {scale_factor:.1f}x")
            elif key == ord('-'):
                scale_factor = max(scale_factor - 0.1, 0.3)
                print(f"Scale: {scale_factor:.1f}x")
            elif key == ord('s'):
                filename = f"screenshot_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(filename, display_frame)
                print(f"Screenshot saved: {filename}")
            elif key == ord(' '):
                paused = not paused
                print("Paused" if paused else "Resumed")
        
        # Cleanup
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print(f"\nProcessed {frame_count} frames")

def main():
    parser = argparse.ArgumentParser(description='Scalable Vision Tracker')
    parser.add_argument('--source', type=str, default=None,
                       help='Video source: camera index (0) or video file path')
    parser.add_argument('--test', action='store_true',
                       help='Run in test mode with synthetic data')
    
    args = parser.parse_args()
    
    # Determine video source
    video_source = None
    test_mode = args.test
    
    if args.source:
        try:
            video_source = int(args.source)
        except ValueError:
            video_source = args.source
    elif not test_mode:
        video_source = 0  # Default camera
    
    # Run tracker
    tracker = ScalableVisionTracker(video_source=video_source, test_mode=test_mode)
    tracker.run()

if __name__ == "__main__":
    main()