"""
Custom Exception Classes

Defines custom exceptions for better error handling and debugging.
"""


class VisionTrackerError(Exception):
    """Base exception for Vision Tracker"""
    pass


class CameraError(VisionTrackerError):
    """Raised when camera operations fail"""
    pass


class ModelLoadError(VisionTrackerError):
    """Raised when model loading fails"""
    pass


class DetectionError(VisionTrackerError):
    """Raised when object detection fails"""
    pass


class ConfigurationError(VisionTrackerError):
    """Raised when configuration is invalid"""
    pass


class DisplayError(VisionTrackerError):
    """Raised when display operations fail"""
    pass


class PlatformError(VisionTrackerError):
    """Raised when platform-specific operations fail"""
    pass