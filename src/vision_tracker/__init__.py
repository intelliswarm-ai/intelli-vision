"""
Vision Tracker Package
"""

from .core.tracker import VisionTracker
from .core.detector import ObjectDetector
from .core.camera import CameraManager
from .utils.config import Config
from .utils.logger import get_logger

__version__ = "1.0.0"
__all__ = ['VisionTracker', 'ObjectDetector', 'CameraManager', 'Config', 'get_logger']