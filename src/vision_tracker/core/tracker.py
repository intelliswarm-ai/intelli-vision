"""
Main Vision Tracker Module

Coordinates all components for real-time object detection and tracking.
"""

import cv2
import numpy as np
import time
import threading
from typing import Optional, Dict, Any, Union, Callable, List
from pathlib import Path
from enum import Enum

from ..utils.logger import LoggerMixin
from ..utils.config import Config
from ..utils.platform import get_platform_info
from ..models.factory import ModelFactory
from .camera import CameraManager, TestFrameGenerator
from .detector import ObjectDetector, DetectionRenderer
from .types import Detection
from .exceptions import VisionTrackerError, CameraError, DisplayError


class TrackerState(Enum):
    """Tracker state enumeration"""
    STOPPED = "stopped"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


class VisionTracker(LoggerMixin):
    """
    Professional Vision Tracking System
    
    Coordinates camera input, object detection, and display output
    for real-time vision tracking applications.
    """
    
    def __init__(self, config: Config, force_headless: bool = False):
        """
        Initialize Vision Tracker
        
        Args:
            config: System configuration object
            force_headless: Force headless mode even if GUI is available
        """
        self.config = config
        self.platform_info = get_platform_info()
        
        # Components
        self.camera_manager: Optional[CameraManager] = None
        self.detector: Optional[ObjectDetector] = None
        self.renderer: Optional[DetectionRenderer] = None
        self.test_generator: Optional[TestFrameGenerator] = None
        
        # Multi-backend support
        self.preloaded_backends: Dict[str, ObjectDetector] = {}
        self.backend_switching_enabled = False
        self.available_backends: List[str] = []
        self.current_backend_index = 0
        
        # State
        self.state = TrackerState.STOPPED
        self.is_test_mode = False
        self.frame_count = 0
        self.start_time = 0.0
        
        # Display
        self.window_name = "Vision Tracker - Professional"
        self.display_available = self.platform_info.has_gui and not force_headless
        
        # Threading
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._processing_thread: Optional[threading.Thread] = None
        
        # Statistics
        self.fps_history = []
        self.detection_stats = {}
        
        # Callbacks
        self.on_detection_callback: Optional[Callable] = None
        self.on_frame_callback: Optional[Callable] = None
        
        self.logger.info(f"VisionTracker initialized on {self.platform_info.system}")
        self.logger.info(f"Display available: {self.display_available}")
    
    def initialize(self, 
                  source: Union[int, str, Path] = None,
                  test_mode: bool = False,
                  model_path: Optional[str] = None,
                  preload_backends: Optional[List[str]] = None) -> bool:
        """
        Initialize the vision tracking system
        
        Args:
            source: Video source (camera index, file path, or None for test mode)
            test_mode: Force test mode with synthetic data
            model_path: Custom model path (optional)
            preload_backends: List of backends to preload for switching (optional)
            
        Returns:
            True if initialization successful
            
        Raises:
            VisionTrackerError: If initialization fails
        """
        self.logger.info("Initializing Vision Tracker...")
        self.state = TrackerState.INITIALIZING
        
        try:
            # Initialize detector(s)
            if preload_backends and len(preload_backends) > 1:
                self._initialize_multiple_backends(preload_backends, model_path)
            else:
                # Single backend mode
                backend_name = self.config.model.backend if self.config.model.backend != "auto" else None
                self.detector = ObjectDetector(self.config.model, backend_name)
                if not self.detector.load_model(model_path, backend_name):
                    raise VisionTrackerError("Failed to load detection model")
            
            # Initialize renderer
            self.renderer = DetectionRenderer(
                font_scale=self.config.display.font_scale,
                line_thickness=self.config.display.line_thickness
            )
            
            # Initialize camera or test generator
            if test_mode or source is None:
                self.is_test_mode = True
                self.test_generator = TestFrameGenerator(
                    width=self.config.camera.width,
                    height=self.config.camera.height,
                    fps=self.config.camera.fps
                )
                self.logger.info("Initialized in test mode")
            else:
                self.is_test_mode = False
                self.camera_manager = CameraManager(self.config.camera)
                
                try:
                    if not self.camera_manager.initialize(source):
                        self.logger.warning("Camera initialization failed, switching to test mode")
                        self.is_test_mode = True
                        self.test_generator = TestFrameGenerator(
                            width=self.config.camera.width,
                            height=self.config.camera.height,
                            fps=self.config.camera.fps
                        )
                except CameraError:
                    self.logger.warning("Camera error, switching to test mode")
                    self.is_test_mode = True
                    self.test_generator = TestFrameGenerator(
                        width=self.config.camera.width,
                        height=self.config.camera.height,
                        fps=self.config.camera.fps
                    )
            
            # Initialize display
            if self.display_available:
                self._initialize_display()
            else:
                self.logger.warning("No display available - running in headless mode")
            
            self.state = TrackerState.STOPPED
            self.logger.info("Vision Tracker initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            self.state = TrackerState.ERROR
            raise VisionTrackerError(f"Initialization failed: {e}")
    
    def _initialize_display(self) -> None:
        """Initialize display window"""
        try:
            cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
            cv2.resizeWindow(self.window_name, 
                           self.config.display.window_width, 
                           self.config.display.window_height)
            
            if self.config.display.fullscreen:
                cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            
            self.logger.debug("Display window initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize display: {e}")
            raise DisplayError(f"Display initialization failed: {e}")
    
    def start(self) -> None:
        """Start the vision tracking system"""
        if self.state != TrackerState.STOPPED:
            self.logger.warning(f"Cannot start - current state: {self.state}")
            return
        
        self.logger.info("Starting Vision Tracker...")
        
        self._stop_event.clear()
        self._pause_event.clear()
        
        self.start_time = time.time()
        self.frame_count = 0
        self.fps_history.clear()
        
        if self.display_available:
            # Run in main thread for GUI
            self._run_main_loop()
        else:
            # Run in separate thread for headless mode
            self._processing_thread = threading.Thread(target=self._run_headless_loop, daemon=True)
            self._processing_thread.start()
    
    def stop(self) -> None:
        """Stop the vision tracking system"""
        self.logger.info("Stopping Vision Tracker...")
        
        self._stop_event.set()
        
        if self._processing_thread and self._processing_thread.is_alive():
            self._processing_thread.join(timeout=2.0)
        
        if self.display_available:
            cv2.destroyAllWindows()
        
        self.state = TrackerState.STOPPED
        # Clean up preloaded backends
        for backend_name, detector in self.preloaded_backends.items():
            try:
                # No specific cleanup needed for detectors currently
                pass
            except Exception as e:
                self.logger.warning(f"Error cleaning up {backend_name} backend: {e}")
        
        self.preloaded_backends.clear()
        
        self.logger.info("Vision Tracker stopped")
    
    def pause(self) -> None:
        """Pause the vision tracking system"""
        if self.state == TrackerState.RUNNING:
            self._pause_event.set()
            self.state = TrackerState.PAUSED
            self.logger.info("Vision Tracker paused")
    
    def resume(self) -> None:
        """Resume the vision tracking system"""
        if self.state == TrackerState.PAUSED:
            self._pause_event.clear()
            self.state = TrackerState.RUNNING
            self.logger.info("Vision Tracker resumed")
    
    def _run_main_loop(self) -> None:
        """Main processing loop with GUI"""
        self.state = TrackerState.RUNNING
        
        while not self._stop_event.is_set():
            try:
                # Check for pause
                if self._pause_event.is_set():
                    self.state = TrackerState.PAUSED
                    time.sleep(0.1)
                    continue
                elif self.state == TrackerState.PAUSED:
                    self.state = TrackerState.RUNNING
                
                # Process frame
                frame_data = self._process_frame()
                if frame_data is None:
                    continue
                
                frame, detections = frame_data
                
                # Display frame
                cv2.imshow(self.window_name, frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if not self._handle_key_input(key):
                    break
                
                # Update statistics
                self._update_stats(detections)
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                self.state = TrackerState.ERROR
                break
        
        self.stop()
    
    def _run_headless_loop(self) -> None:
        """Headless processing loop"""
        self.state = TrackerState.RUNNING
        
        while not self._stop_event.is_set():
            try:
                # Check for pause
                if self._pause_event.is_set():
                    self.state = TrackerState.PAUSED
                    time.sleep(0.1)
                    continue
                elif self.state == TrackerState.PAUSED:
                    self.state = TrackerState.RUNNING
                
                # Process frame
                frame_data = self._process_frame()
                if frame_data is None:
                    time.sleep(0.033)  # ~30 FPS
                    continue
                
                frame, detections = frame_data
                
                # Save frame periodically (for debugging)
                if self.frame_count % 300 == 0:  # Every 10 seconds at 30 FPS
                    output_path = f"output_frame_{self.frame_count:06d}.jpg"
                    cv2.imwrite(output_path, frame)
                    self.logger.info(f"Saved frame: {output_path}")
                
                # Update statistics
                self._update_stats(detections)
                
                time.sleep(0.033)  # ~30 FPS
                
            except Exception as e:
                self.logger.error(f"Error in headless loop: {e}")
                self.state = TrackerState.ERROR
                break
    
    def _process_frame(self) -> Optional[tuple]:
        """Process a single frame"""
        # Get frame
        if self.is_test_mode:
            if self.test_generator is None:
                return None
            frame = self.test_generator.generate_frame()
        else:
            if self.camera_manager is None:
                return None
            success, frame = self.camera_manager.read_frame()
            if not success or frame is None:
                return None
        
        self.frame_count += 1
        
        # Run detection
        detections = []
        if self.detector and self.detector.is_ready():
            try:
                detections = self.detector.detect(frame)
            except Exception as e:
                self.logger.error(f"Detection error: {e}")
        
        # Render results
        if self.renderer:
            frame = self.renderer.render_detections(frame, detections)
            
            # Add info overlay
            if self.config.display.show_fps or self.config.display.show_confidence:
                info = self._get_info_overlay()
                frame = self.renderer.add_info_overlay(frame, info)
        
        # Call callbacks
        if self.on_frame_callback:
            try:
                self.on_frame_callback(frame, detections)
            except Exception as e:
                self.logger.error(f"Frame callback error: {e}")
        
        if self.on_detection_callback and detections:
            try:
                self.on_detection_callback(detections)
            except Exception as e:
                self.logger.error(f"Detection callback error: {e}")
        
        return frame, detections
    
    def _get_info_overlay(self) -> Dict[str, Any]:
        """Get information overlay data"""
        info = {}
        
        if self.config.display.show_fps:
            current_fps = self.get_current_fps()
            info['FPS'] = f"{current_fps:.1f}"
        
        if self.detector:
            avg_inference_time = self.detector.get_average_inference_time()
            info['Inference'] = f"{avg_inference_time*1000:.1f}ms"
        
        info['Frame'] = self.frame_count
        info['Mode'] = "Test" if self.is_test_mode else "Live"
        
        # Add backend info
        if self.detector:
            backend_name = self.detector.get_backend_name() or "Unknown"
            info['Backend'] = backend_name.upper()
            
            # Show switching info if multiple backends available
            if self.backend_switching_enabled and len(self.available_backends) > 1:
                info['Backends'] = f"({self.current_backend_index + 1}/{len(self.available_backends)})"
        
        return info
    
    def _handle_key_input(self, key: int) -> bool:
        """
        Handle keyboard input
        
        Returns:
            False to exit, True to continue
        """
        if key == ord('q') or key == 27:  # 'q' or Escape
            return False
        elif key == ord(' '):  # Space - pause/resume
            if self.state == TrackerState.RUNNING:
                self.pause()
            elif self.state == TrackerState.PAUSED:
                self.resume()
        elif key == ord('s'):  # Save screenshot
            self._save_screenshot()
        elif key == ord('f'):  # Toggle fullscreen
            self._toggle_fullscreen()
        elif key == ord('r'):  # Reset window
            self._reset_window()
        elif key == ord('1'):  # Switch to backend 1
            self._switch_backend(0)
        elif key == ord('2'):  # Switch to backend 2
            self._switch_backend(1)
        elif key == ord('3'):  # Switch to backend 3
            self._switch_backend(2)
        elif key == ord('n'):  # Next backend
            self._switch_to_next_backend()
        elif key == ord('b'):  # Previous backend
            self._switch_to_previous_backend()
        elif key == ord('i'):  # Show backend info
            self._show_backend_info()
        
        return True
    
    def _save_screenshot(self) -> None:
        """Save current frame as screenshot"""
        if self.is_test_mode and self.test_generator:
            frame = self.test_generator.generate_frame()
        elif self.camera_manager:
            frame = self.camera_manager.get_last_frame()
        else:
            return
        
        if frame is not None:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"screenshot_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            self.logger.info(f"Screenshot saved: {filename}")
    
    def _toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode"""
        try:
            current_prop = cv2.getWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN)
            if current_prop == cv2.WINDOW_FULLSCREEN:
                cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                self.logger.info("Fullscreen OFF")
            else:
                cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                self.logger.info("Fullscreen ON")
        except Exception as e:
            self.logger.error(f"Failed to toggle fullscreen: {e}")
    
    def _reset_window(self) -> None:
        """Reset window to default size"""
        try:
            cv2.resizeWindow(self.window_name, 
                           self.config.display.window_width, 
                           self.config.display.window_height)
            self.logger.info("Window size reset")
        except Exception as e:
            self.logger.error(f"Failed to reset window: {e}")
    
    def _update_stats(self, detections: list) -> None:
        """Update tracking statistics"""
        # Update FPS history
        current_time = time.time()
        elapsed = current_time - self.start_time
        if elapsed > 0:
            current_fps = self.frame_count / elapsed
            self.fps_history.append(current_fps)
            
            # Keep only recent history
            if len(self.fps_history) > 100:
                self.fps_history = self.fps_history[-50:]
        
        # Update detection statistics
        for detection in detections:
            class_name = detection.class_name
            if class_name not in self.detection_stats:
                self.detection_stats[class_name] = 0
            self.detection_stats[class_name] += 1
    
    def get_current_fps(self) -> float:
        """Get current FPS"""
        if not self.fps_history:
            return 0.0
        return self.fps_history[-1]
    
    def get_average_fps(self) -> float:
        """Get average FPS"""
        if not self.fps_history:
            return 0.0
        return sum(self.fps_history) / len(self.fps_history)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        return {
            'state': self.state.value,
            'frame_count': self.frame_count,
            'runtime': time.time() - self.start_time if self.start_time > 0 else 0,
            'current_fps': self.get_current_fps(),
            'average_fps': self.get_average_fps(),
            'detection_stats': self.detection_stats.copy(),
            'model_info': self.detector.get_model_info() if self.detector else {},
            'camera_info': {
                'resolution': self.camera_manager.get_resolution() if self.camera_manager else (0, 0),
                'is_test_mode': self.is_test_mode
            }
        }
    
    def set_detection_callback(self, callback: Callable) -> None:
        """Set detection callback function"""
        self.on_detection_callback = callback
    
    def set_frame_callback(self, callback: Callable) -> None:
        """Set frame callback function"""
        self.on_frame_callback = callback
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
        
        if self.camera_manager:
            self.camera_manager.release()
    
    def _initialize_multiple_backends(self, backend_names: List[str], model_path: Optional[str] = None) -> None:
        """Initialize multiple backends for dynamic switching"""
        self.logger.info(f"Preloading backends: {backend_names}")
        
        successful_backends = []
        
        for backend_name in backend_names:
            try:
                self.logger.info(f"Loading {backend_name} backend...")
                detector = ObjectDetector(self.config.model, backend_name)
                
                if detector.load_model(model_path, backend_name):
                    self.preloaded_backends[backend_name] = detector
                    successful_backends.append(backend_name)
                    self.logger.info(f"✓ {backend_name} backend loaded successfully")
                else:
                    self.logger.warning(f"✗ Failed to load {backend_name} backend")
                    
            except Exception as e:
                self.logger.warning(f"✗ Failed to initialize {backend_name} backend: {e}")
        
        if not successful_backends:
            raise VisionTrackerError("No backends loaded successfully")
        
        # Set up backend switching
        self.available_backends = successful_backends
        self.backend_switching_enabled = True
        self.current_backend_index = 0
        
        # Set current detector to first successful backend
        self.detector = self.preloaded_backends[successful_backends[0]]
        
        self.logger.info(f"Backend switching enabled with {len(successful_backends)} backends: {successful_backends}")
        self.logger.info(f"Current backend: {successful_backends[0]}")
    
    def _switch_backend(self, backend_index: int) -> None:
        """Switch to backend at specified index"""
        if not self.backend_switching_enabled:
            self.logger.warning("Backend switching not enabled")
            return
        
        if backend_index < 0 or backend_index >= len(self.available_backends):
            self.logger.warning(f"Invalid backend index: {backend_index}")
            return
        
        old_backend = self.available_backends[self.current_backend_index]
        new_backend = self.available_backends[backend_index]
        
        if old_backend == new_backend:
            self.logger.info(f"Already using {new_backend} backend")
            return
        
        # Switch detector
        self.detector = self.preloaded_backends[new_backend]
        self.current_backend_index = backend_index
        
        self.logger.info(f"Switched from {old_backend} to {new_backend} backend")
    
    def _switch_to_next_backend(self) -> None:
        """Switch to next backend in the list"""
        if not self.backend_switching_enabled:
            return
        
        next_index = (self.current_backend_index + 1) % len(self.available_backends)
        self._switch_backend(next_index)
    
    def _switch_to_previous_backend(self) -> None:
        """Switch to previous backend in the list"""
        if not self.backend_switching_enabled:
            return
        
        prev_index = (self.current_backend_index - 1) % len(self.available_backends)
        self._switch_backend(prev_index)
    
    def _show_backend_info(self) -> None:
        """Show detailed backend information"""
        if not self.detector:
            self.logger.info("No detector loaded")
            return
        
        info = self.detector.get_model_info()
        self.logger.info("=== BACKEND INFORMATION ===")
        for key, value in info.items():
            self.logger.info(f"  {key}: {value}")
        
        if self.backend_switching_enabled:
            self.logger.info(f"Available backends: {self.available_backends}")
            current_backend = self.available_backends[self.current_backend_index]
            self.logger.info(f"Current backend: {current_backend} ({self.current_backend_index + 1}/{len(self.available_backends)})")
    
    def switch_backend_by_name(self, backend_name: str) -> bool:
        """Switch to backend by name (API method)"""
        if not self.backend_switching_enabled:
            self.logger.warning("Backend switching not enabled")
            return False
        
        if backend_name not in self.available_backends:
            self.logger.warning(f"Backend {backend_name} not available. Available: {self.available_backends}")
            return False
        
        backend_index = self.available_backends.index(backend_name)
        self._switch_backend(backend_index)
        return True
    
    def get_current_backend(self) -> Optional[str]:
        """Get name of current backend"""
        if not self.detector:
            return None
        return self.detector.get_backend_name()
    
    def get_available_backends(self) -> List[str]:
        """Get list of available backends"""
        if self.backend_switching_enabled:
            return self.available_backends.copy()
        elif self.detector:
            backend = self.detector.get_backend_name()
            return [backend] if backend else []
        else:
            return []
    
    def is_backend_switching_enabled(self) -> bool:
        """Check if backend switching is enabled"""
        return self.backend_switching_enabled
    
    def __del__(self):
        """Destructor"""
        self.stop()