"""
Camera Management Module

Handles camera initialization, configuration, and frame capture across different platforms.
"""

import cv2
import numpy as np
import threading
import time
from typing import Optional, Tuple, List, Union
from pathlib import Path

from ..utils.logger import LoggerMixin
from ..utils.platform import get_platform_info, PlatformDetector
from ..utils.config import CameraConfig
from .exceptions import CameraError


class CameraManager(LoggerMixin):
    """
    Professional camera management with multi-platform support
    """
    
    def __init__(self, config: CameraConfig):
        """
        Initialize camera manager
        
        Args:
            config: Camera configuration object
        """
        self.config = config
        self.platform_info = get_platform_info()
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_opened = False
        self.frame_count = 0
        self.last_frame: Optional[np.ndarray] = None
        self.last_frame_time = 0.0
        self._lock = threading.Lock()
        
        self.logger.info(f"CameraManager initialized for {self.platform_info.system}")
    
    def initialize(self, source: Union[int, str, Path] = None) -> bool:
        """
        Initialize camera with the given source
        
        Args:
            source: Camera source (index, device path, or video file)
            
        Returns:
            True if initialization successful, False otherwise
            
        Raises:
            CameraError: If camera cannot be initialized
        """
        if source is None:
            source = self.config.device_index
        
        self.logger.info(f"Initializing camera with source: {source}")
        
        try:
            # Handle different source types
            if isinstance(source, (str, Path)):
                source_path = Path(source)
                if source_path.exists():
                    self.logger.info(f"Using video file: {source_path}")
                    self.cap = cv2.VideoCapture(str(source_path))
                else:
                    raise CameraError(f"Video file not found: {source_path}")
            else:
                # Camera device
                self.cap = self._initialize_camera_device(source)
            
            if not self.cap or not self.cap.isOpened():
                raise CameraError(f"Failed to open camera source: {source}")
            
            # Configure camera settings
            self._configure_camera()
            
            # Test frame capture
            ret, frame = self.cap.read()
            if not ret or frame is None:
                raise CameraError("Failed to capture test frame")
            
            self.is_opened = True
            self.last_frame = frame
            self.last_frame_time = time.time()
            
            # Log camera info
            self._log_camera_info()
            
            self.logger.info("Camera initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Camera initialization failed: {e}")
            self.release()
            raise CameraError(f"Camera initialization failed: {e}")
    
    def _initialize_camera_device(self, device_index: int) -> cv2.VideoCapture:
        """Initialize camera device with platform-specific backends"""
        backends = PlatformDetector.get_camera_backends()
        
        for backend_name, backend_id in backends:
            self.logger.debug(f"Trying {backend_name} backend...")
            
            try:
                cap = cv2.VideoCapture(device_index, backend_id)
                if cap.isOpened():
                    # Test if we can actually read a frame
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        self.logger.info(f"Camera opened successfully with {backend_name} backend")
                        return cap
                    else:
                        cap.release()
                        self.logger.debug(f"{backend_name} backend opened but failed to read frame")
                else:
                    self.logger.debug(f"{backend_name} backend failed to open")
            except Exception as e:
                self.logger.debug(f"{backend_name} backend error: {e}")
        
        # Try alternative device indices
        self.logger.info("Trying alternative camera indices...")
        for i in range(5):
            if i == device_index:
                continue
                
            self.logger.debug(f"Trying camera index {i}...")
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        self.logger.info(f"Found working camera at index {i}")
                        self.config.device_index = i
                        return cap
                    else:
                        cap.release()
            except Exception as e:
                self.logger.debug(f"Camera index {i} failed: {e}")
        
        raise CameraError("No working camera found")
    
    def _configure_camera(self) -> None:
        """Configure camera settings"""
        if not self.cap:
            return
        
        try:
            # Set resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
            
            # Set FPS
            self.cap.set(cv2.CAP_PROP_FPS, self.config.fps)
            
            # Additional optimizations
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer lag
            
            self.logger.debug("Camera settings configured")
            
        except Exception as e:
            self.logger.warning(f"Failed to configure camera settings: {e}")
    
    def _log_camera_info(self) -> None:
        """Log camera information"""
        if not self.cap:
            return
        
        try:
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            backend = self.cap.getBackendName()
            
            self.logger.info(f"Camera info - Resolution: {width}x{height}, FPS: {fps:.1f}, Backend: {backend}")
            
        except Exception as e:
            self.logger.debug(f"Could not retrieve camera info: {e}")
    
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read a frame from the camera
        
        Returns:
            Tuple of (success, frame)
        """
        if not self.is_opened or not self.cap:
            return False, None
        
        with self._lock:
            try:
                ret, frame = self.cap.read()
                
                if ret and frame is not None:
                    self.frame_count += 1
                    self.last_frame = frame.copy()
                    self.last_frame_time = time.time()
                    return True, frame
                else:
                    self.logger.warning("Failed to read frame from camera")
                    return False, None
                    
            except Exception as e:
                self.logger.error(f"Error reading frame: {e}")
                return False, None
    
    def get_last_frame(self) -> Optional[np.ndarray]:
        """Get the last successfully captured frame"""
        with self._lock:
            return self.last_frame.copy() if self.last_frame is not None else None
    
    def get_frame_rate(self) -> float:
        """Get actual frame rate"""
        if not self.cap:
            return 0.0
        
        try:
            return self.cap.get(cv2.CAP_PROP_FPS)
        except Exception:
            return 0.0
    
    def get_resolution(self) -> Tuple[int, int]:
        """Get current camera resolution"""
        if not self.cap:
            return (0, 0)
        
        try:
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return (width, height)
        except Exception:
            return (0, 0)
    
    def is_ready(self) -> bool:
        """Check if camera is ready for capture"""
        return self.is_opened and self.cap is not None and self.cap.isOpened()
    
    def release(self) -> None:
        """Release camera resources"""
        with self._lock:
            if self.cap:
                try:
                    self.cap.release()
                    self.logger.info("Camera released")
                except Exception as e:
                    self.logger.error(f"Error releasing camera: {e}")
                finally:
                    self.cap = None
                    self.is_opened = False
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.release()
    
    def __del__(self):
        """Destructor"""
        self.release()


class TestFrameGenerator(LoggerMixin):
    """
    Generates synthetic test frames for testing and demonstration
    """
    
    def __init__(self, width: int = 640, height: int = 480, fps: float = 30.0):
        """
        Initialize test frame generator
        
        Args:
            width: Frame width
            height: Frame height
            fps: Target frame rate
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.frame_interval = 1.0 / fps
        self.frame_count = 0
        self.start_time = time.time()
        
        self.logger.info(f"TestFrameGenerator initialized: {width}x{height} @ {fps} FPS")
    
    def generate_frame(self) -> np.ndarray:
        """
        Generate a synthetic test frame with moving objects
        
        Returns:
            Generated frame as numpy array
        """
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Current time for animations
        current_time = time.time() - self.start_time
        
        # Gradient background
        for i in range(self.height):
            intensity = int(50 + 100 * (i / self.height))
            frame[i, :] = [intensity // 3, intensity // 2, intensity]
        
        # Moving elements
        self._add_moving_circle(frame, current_time)
        self._add_moving_rectangle(frame, current_time)
        self._add_grid_pattern(frame)
        self._add_text_overlays(frame, current_time)
        
        self.frame_count += 1
        return frame
    
    def _add_moving_circle(self, frame: np.ndarray, t: float) -> None:
        """Add animated circle to frame"""
        cx = int(self.width // 2 + (self.width // 4) * np.sin(t * 0.5))
        cy = int(self.height // 2 + (self.height // 4) * np.cos(t * 0.7))
        radius = int(30 + 20 * np.sin(t * 2))
        
        cv2.circle(frame, (cx, cy), radius, (100, 200, 100), -1)
        cv2.circle(frame, (cx, cy), radius + 5, (255, 255, 255), 2)
    
    def _add_moving_rectangle(self, frame: np.ndarray, t: float) -> None:
        """Add animated rectangle to frame"""
        x = int((self.width + 100) * (t * 0.1 % 1) - 50)
        y = int(self.height * 0.7)
        w, h = 80, 40
        
        cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 200), -1)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)
    
    def _add_grid_pattern(self, frame: np.ndarray) -> None:
        """Add grid pattern for scale reference"""
        grid_spacing = 80
        color = (80, 80, 80)
        
        for x in range(0, self.width, grid_spacing):
            cv2.line(frame, (x, 0), (x, self.height), color, 1)
        
        for y in range(0, self.height, grid_spacing):
            cv2.line(frame, (0, y), (self.width, y), color, 1)
    
    def _add_text_overlays(self, frame: np.ndarray, t: float) -> None:
        """Add text information to frame"""
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Title
        cv2.putText(frame, "TEST MODE - Synthetic Data", (10, 30),
                   font, 0.8, (255, 255, 255), 2)
        
        # Frame info
        cv2.putText(frame, f"Frame: {self.frame_count}", (10, 60),
                   font, 0.6, (200, 200, 200), 1)
        
        # Time info
        cv2.putText(frame, f"Time: {t:.1f}s", (10, 85),
                   font, 0.6, (200, 200, 200), 1)
        
        # Resolution info
        cv2.putText(frame, f"Resolution: {self.width}x{self.height}", (10, self.height - 40),
                   font, 0.5, (255, 255, 255), 1)
        
        # FPS info
        fps = self.frame_count / t if t > 0 else 0
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, self.height - 15),
                   font, 0.5, (0, 255, 0), 1)