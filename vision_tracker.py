import cv2
import numpy as np
import torch
import os
import sys
import platform
import time
import argparse
from pathlib import Path
from ultralytics import YOLO

# Handle torch.load compatibility for different PyTorch versions
try:
    _original_torch_load = torch.load
    
    def patched_torch_load(*args, **kwargs):
        # Force weights_only=False for YOLO model loading (safe for official YOLO weights)
        if 'weights_only' not in kwargs:
            kwargs['weights_only'] = False
        return _original_torch_load(*args, **kwargs)
    
    torch.load = patched_torch_load
except Exception as e:
    print(f"Warning: Could not patch torch.load: {e}")
    # Continue anyway - older PyTorch versions don't have this issue

def detect_platform():
    """Detect the current platform"""
    system = platform.system()
    is_wsl = 'microsoft' in platform.uname().release.lower()
    return {
        'system': system,
        'is_wsl': is_wsl,
        'is_windows': system == 'Windows',
        'is_linux': system == 'Linux' and not is_wsl,
        'platform_name': 'WSL' if is_wsl else system
    }

class VisionTracker:
    def __init__(self, model_path="yolov8n.pt", video_source=None, use_test_mode=False):
        platform_info = detect_platform()
        is_docker = os.path.exists('/.dockerenv')
        
        print(f"Running on: {platform_info['platform_name']}")
        if is_docker:
            print("Running inside Docker container")
        
        # Initialize YOLO model with error handling
        try:
            print(f"Loading YOLO model: {model_path}")
            if not os.path.exists(model_path) and not model_path.startswith('yolov8'):
                print(f"Model file not found: {model_path}")
                model_path = 'yolov8n.pt'  # Fallback to default
                print(f"Using default model: {model_path}")
            
            self.model = YOLO(model_path)
            print("✓ YOLO model loaded successfully")
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            print("This might be due to:")
            print("  - Missing dependencies (run fix_yolo_dependencies.bat)")
            print("  - Network issues downloading model")
            print("  - Incompatible model file")
            raise
        self.video_source = video_source
        self.test_mode = use_test_mode
        self.cap = None
        self.is_docker = is_docker
        
        # Initialize video capture based on source
        if self.test_mode:
            print("Running in test mode with generated frames")
            self.cap = None
        elif video_source is not None:
            # Check if video_source is a file
            if isinstance(video_source, str) and Path(video_source).exists():
                print(f"Using video file: {video_source}")
                self.cap = cv2.VideoCapture(video_source)
            else:
                # Try to use camera
                self._initialize_camera(video_source if isinstance(video_source, int) else 0, platform_info)
        
    def _initialize_camera(self, camera_index, platform_info):
        """Initialize camera based on platform"""
        # In Docker, camera access is often problematic
        if self.is_docker:
            print("Docker environment detected - checking for camera devices...")
            # Check if video devices exist
            video_devices = [f"/dev/video{i}" for i in range(10) if os.path.exists(f"/dev/video{i}")]
            if not video_devices:
                print("No video devices found in Docker container")
                print("To use a camera in Docker:")
                print("  1. Ensure camera is connected to host")
                print("  2. Run with: docker run --device=/dev/video0 ...")
                print("  3. Or use privileged mode: docker run --privileged ...")
                self.test_mode = True
                return
            else:
                print(f"Found video devices: {video_devices}")
        
        # Platform-specific camera initialization
        if platform_info['is_wsl']:
            print("WSL detected - Camera access may require USB passthrough")
            self.cap = cv2.VideoCapture(camera_index)
        elif platform_info['is_windows']:
            print("Windows detected - Trying camera access...")
            # Try DirectShow first
            self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                print("DirectShow failed, trying default backend...")
                self.cap = cv2.VideoCapture(camera_index)
            if not self.cap.isOpened():
                print("Default backend failed, trying Windows Media Foundation...")
                self.cap = cv2.VideoCapture(camera_index, cv2.CAP_MSMF)
        else:
            print("Linux detected - Using V4L2 for camera access")
            self.cap = cv2.VideoCapture(camera_index, cv2.CAP_V4L2)
            if not self.cap.isOpened():
                self.cap = cv2.VideoCapture(camera_index)
        
        # Try alternative camera indices if failed
        if not self.cap or not self.cap.isOpened():
            print("\nTrying alternative camera indices...")
            for i in range(5):
                print(f"  Checking camera index {i}...", end=" ")
                if platform_info['is_windows']:
                    # Try multiple backends for Windows
                    for backend_name, backend in [("MSMF", cv2.CAP_MSMF), ("DSHOW", cv2.CAP_DSHOW), ("Default", cv2.CAP_ANY)]:
                        self.cap = cv2.VideoCapture(i, backend)
                        if self.cap.isOpened():
                            print(f"✓ Found with {backend_name} backend!")
                            camera_index = i
                            break
                else:
                    self.cap = cv2.VideoCapture(i)
                    if self.cap.isOpened():
                        print("✓ Found!")
                        camera_index = i
                        break
                
                if self.cap and self.cap.isOpened():
                    break
                else:
                    print("✗ Not available")
            else:
                print("\n" + "="*50)
                print("No camera detected!")
                print("="*50)
                print("\nPossible reasons:")
                print("  • Camera is being used by another application")
                print("  • Camera drivers are not installed")
                print("  • Camera is disabled in Device Manager")
                print("  • Privacy settings blocking camera access")
                print("\nRunning in TEST MODE with synthetic data...")
                print("="*50)
                self.cap = None
                self.test_mode = True
        
        if self.cap and self.cap.isOpened():
            self.test_mode = False
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            print(f"Camera initialized successfully")
        
    def generate_test_frame(self):
        """Generate synthetic test frames with moving objects"""
        # Create a test frame with some shapes to detect
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Add gradient background
        for i in range(480):
            frame[i, :] = [30 + i//4, 20 + i//6, 10 + i//8]
        
        # Add moving objects based on time
        import random
        t = time.time()
        
        # Moving circle (simulates a person)
        cx = int(320 + 200 * np.sin(t))
        cy = int(240 + 100 * np.cos(t * 0.7))
        cv2.circle(frame, (cx, cy), 40, (100, 200, 100), -1)
        cv2.circle(frame, (cx, cy - 60), 25, (200, 150, 100), -1)  # Head
        
        # Moving rectangle (simulates a car)
        rx = int(100 + 400 * ((t * 0.3) % 1))
        ry = 350
        cv2.rectangle(frame, (rx, ry), (rx + 80, ry + 40), (50, 50, 200), -1)
        
        # Static object (simulates a chair)
        cv2.rectangle(frame, (500, 300), (580, 400), (139, 69, 19), -1)
        
        # Add noise for realism
        noise = np.random.normal(0, 5, frame.shape).astype(np.uint8)
        frame = cv2.add(frame, noise)
        
        # Add text overlay
        cv2.putText(frame, "TEST MODE - Synthetic Data", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, f"Time: {time.strftime('%H:%M:%S')}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        return frame
    
    def draw_detections(self, frame, results):
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                    confidence = float(box.conf[0].cpu().numpy())
                    class_id = int(box.cls[0].cpu().numpy())
                    class_name = self.model.names[class_id]
                    
                    if confidence > 0.5:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        
                        label = f"{class_name}: {confidence:.2f}"
                        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                        
                        cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                                    (x1 + label_size[0], y1), (0, 255, 0), -1)
                        cv2.putText(frame, label, (x1, y1 - 5), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        return frame
    
    def run(self):
        print("Starting real-time object detection.")
        print("Controls:")
        print("  'q' - Quit")
        print("  's' - Save screenshot")
        print("  'f' - Toggle fullscreen")
        print("  'r' - Reset window size")
        print("  SPACE - Pause/Resume")
        
        frame_count = 0
        fps_time = time.time()
        fps = 0
        paused = False
        fullscreen = False
        
        # Create a resizable window
        window_name = 'Vision Tracker - Real-time Object Detection'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 960, 720)  # Set initial size
        
        while True:
            if not paused:
                if self.test_mode:
                    frame = self.generate_test_frame()
                    ret = True
                    time.sleep(0.033)  # Simulate 30 FPS
                else:
                    ret, frame = self.cap.read()
                    if not ret:
                        if isinstance(self.video_source, str) and Path(self.video_source).exists():
                            # Loop video file
                            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                            continue
                        else:
                            print("Failed to grab frame")
                            break
                
                # Run detection
                results = self.model(frame, verbose=False)
                frame_with_detections = self.draw_detections(frame, results)
            else:
                # When paused, keep showing the last frame
                if 'frame_with_detections' not in locals():
                    frame_with_detections = frame
                # Add pause indicator
                cv2.putText(frame_with_detections, "PAUSED", 
                           (frame_with_detections.shape[1]//2 - 50, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
            
            # Calculate FPS
            frame_count += 1
            if frame_count % 30 == 0:
                fps = 30 / (time.time() - fps_time)
                fps_time = time.time()
            
            # Add FPS counter
            cv2.putText(frame_with_detections, f"FPS: {fps:.1f}", (10, frame.shape[0] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Get current window size and resize frame to fit
            try:
                # Get window properties
                window_rect = cv2.getWindowImageRect(window_name)
                if window_rect[2] > 0 and window_rect[3] > 0:
                    # Resize frame to match window size while maintaining aspect ratio
                    h, w = frame_with_detections.shape[:2]
                    window_width, window_height = window_rect[2], window_rect[3]
                    
                    # Calculate scaling factor to fit frame in window
                    scale = min(window_width / w, window_height / h)
                    new_width = int(w * scale)
                    new_height = int(h * scale)
                    
                    # Resize the frame
                    if new_width != w or new_height != h:
                        frame_with_detections = cv2.resize(frame_with_detections, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
                        
                        # Center the frame if aspect ratios don't match
                        if new_width < window_width or new_height < window_height:
                            # Create black background
                            background = np.zeros((window_height, window_width, 3), dtype=np.uint8)
                            # Calculate position to center the frame
                            y_offset = (window_height - new_height) // 2
                            x_offset = (window_width - new_width) // 2
                            # Place frame on background
                            background[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = frame_with_detections
                            frame_with_detections = background
            except:
                # If getWindowImageRect is not available (older OpenCV), use default behavior
                pass
            
            # Show frame in the resizable window
            cv2.imshow(window_name, frame_with_detections)
            
            # Check for keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Save screenshot
                filename = f"screenshot_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(filename, frame_with_detections)
                print(f"Screenshot saved: {filename}")
            elif key == ord('f'):
                # Toggle fullscreen
                fullscreen = not fullscreen
                if fullscreen:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                    print("Fullscreen mode ON")
                else:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                    print("Fullscreen mode OFF")
            elif key == ord('r'):
                # Reset window size
                cv2.resizeWindow(window_name, 960, 720)
                print("Window size reset")
            elif key == ord(' '):
                # Toggle pause
                paused = not paused
                print("Paused" if paused else "Resumed")
        
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

def main():
    parser = argparse.ArgumentParser(description='Vision Tracker - Real-time Object Detection')
    parser.add_argument('--source', type=str, default=None,
                       help='Video source: camera index (0), video file path, or None for test mode')
    parser.add_argument('--model', type=str, default='yolov8n.pt',
                       help='Path to YOLO model file')
    parser.add_argument('--test', action='store_true',
                       help='Run in test mode with synthetic data')
    
    args = parser.parse_args()
    
    # Determine video source
    video_source = None
    use_test = args.test
    
    if args.source:
        # Check if source is a number (camera index)
        try:
            video_source = int(args.source)
        except ValueError:
            # Assume it's a file path
            video_source = args.source
    elif not args.test:
        # Default to camera 0 if not in test mode
        video_source = 0
    
    try:
        print("="*50)
        print("Vision Tracker - Object Detection System")
        print("="*50)
        print(f"Model: {args.model}")
        if use_test:
            print("Mode: Test (Synthetic Data)")
        elif video_source is not None:
            if isinstance(video_source, int):
                print(f"Source: Camera {video_source}")
            else:
                print(f"Source: {video_source}")
        print("Controls:")
        print("  'q' - Quit")
        print("  's' - Save screenshot")
        print("="*50)
        
        tracker = VisionTracker(model_path=args.model, video_source=video_source, use_test_mode=use_test)
        tracker.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()