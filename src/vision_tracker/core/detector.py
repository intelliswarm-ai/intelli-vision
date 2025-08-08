"""
Object Detection Module

Handles YOLO model loading, inference, and result processing.
"""

import cv2
import numpy as np
import torch
import time
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
from dataclasses import dataclass

from ..utils.logger import LoggerMixin
from ..utils.config import ModelConfig
from ..utils.platform import get_platform_info
from ..models.factory import ModelFactory
from ..models.base import BaseDetectionModel
from .exceptions import ModelLoadError, DetectionError
from .types import Detection




class ObjectDetector(LoggerMixin):
    """
    Professional object detection with multiple backend support
    """
    
    def __init__(self, config: ModelConfig, backend_name: Optional[str] = None):
        """
        Initialize object detector
        
        Args:
            config: Model configuration object
            backend_name: Detection backend to use (auto-detect if None)
        """
        self.config = config
        self.backend_name = backend_name
        self.backend_model: Optional[BaseDetectionModel] = None
        self.is_loaded = False
        
        self.logger.info(f"ObjectDetector initialized")
    
    def load_model(self, model_path: Optional[str] = None, backend_name: Optional[str] = None) -> bool:
        """
        Load detection model using specified or auto-detected backend
        
        Args:
            model_path: Path to model file (optional, uses config if not provided)
            backend_name: Backend to use (optional, auto-detect if not provided)
            
        Returns:
            True if model loaded successfully
            
        Raises:
            ModelLoadError: If model loading fails
        """
        if model_path is None:
            model_path = self.config.name
        
        if backend_name is None:
            backend_name = self.backend_name
        
        if backend_name is None:
            # Auto-detect backend
            try:
                backend_name = ModelFactory.auto_detect_backend()
            except ModelLoadError as e:
                self.logger.error(f"Backend auto-detection failed: {e}")
                raise
        
        self.logger.info(f"Loading model with {backend_name} backend: {model_path}")
        
        try:
            # Create backend model
            backend_config = {
                'device': self.config.device,
                'confidence_threshold': self.config.confidence_threshold,
                'iou_threshold': self.config.iou_threshold
            }
            
            self.backend_model = ModelFactory.create_model(backend_name, backend_config)
            self.backend_name = backend_name
            
            # Load the model
            if not self.backend_model.load_model(model_path):
                raise ModelLoadError("Backend failed to load model")
            
            self.is_loaded = True
            
            self.logger.info(f"Model loaded successfully with {backend_name} backend")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise ModelLoadError(f"Model loading failed: {e}")
    
    def detect(self, frame: np.ndarray) -> List[Detection]:
        """
        Perform object detection on frame
        
        Args:
            frame: Input frame as numpy array
            
        Returns:
            List of Detection objects
            
        Raises:
            DetectionError: If detection fails
        """
        if not self.is_loaded or self.backend_model is None:
            raise DetectionError("Model not loaded")
        
        try:
            return self.backend_model.detect(frame)
        except Exception as e:
            self.logger.error(f"Detection failed: {e}")
            raise DetectionError(f"Detection failed: {e}")
    
    def get_average_inference_time(self) -> float:
        """Get average inference time"""
        if not self.backend_model:
            return 0.0
        return self.backend_model.get_average_inference_time()
    
    def get_fps(self) -> float:
        """Get average FPS based on inference time"""
        if not self.backend_model:
            return 0.0
        return self.backend_model.get_fps()
    
    def is_ready(self) -> bool:
        """Check if detector is ready for inference"""
        return self.is_loaded and self.backend_model is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        if not self.backend_model:
            return {
                'loaded': self.is_loaded,
                'backend': 'None',
                'model_path': self.config.name,
            }
        
        return self.backend_model.get_model_info()
    
    def get_backend_name(self) -> Optional[str]:
        """Get current backend name"""
        return self.backend_name
    
    def get_available_backends(self) -> List[str]:
        """Get list of available backends"""
        return ModelFactory.get_available_backends()
    
    def list_backend_models(self, backend_name: Optional[str] = None) -> Dict[str, str]:
        """List available models for a backend"""
        if backend_name is None:
            backend_name = self.backend_name
        
        if backend_name is None:
            return {}
        
        return ModelFactory.list_models(backend_name)


class DetectionRenderer(LoggerMixin):
    """
    Renders detection results on frames
    """
    
    def __init__(self, font_scale: float = 0.6, line_thickness: int = 2):
        """
        Initialize detection renderer
        
        Args:
            font_scale: Font scale for text
            line_thickness: Thickness of bounding box lines
        """
        self.font_scale = font_scale
        self.line_thickness = line_thickness
        self.colors = self._generate_colors()
        
        self.logger.debug("DetectionRenderer initialized")
    
    def _generate_colors(self) -> Dict[int, Tuple[int, int, int]]:
        """Generate colors for different classes"""
        colors = {}
        for i in range(100):  # Support up to 100 classes
            # Generate distinct colors using HSV
            hue = int(180 * i / 100)
            color_hsv = np.array([[[hue, 255, 255]]], dtype=np.uint8)
            color_bgr = cv2.cvtColor(color_hsv, cv2.COLOR_HSV2BGR)[0, 0]
            colors[i] = tuple(map(int, color_bgr))
        
        return colors
    
    def render_detections(self, frame: np.ndarray, detections: List[Detection]) -> np.ndarray:
        """
        Render detections on frame
        
        Args:
            frame: Input frame
            detections: List of detections to render
            
        Returns:
            Frame with rendered detections
        """
        rendered_frame = frame.copy()
        
        for detection in detections:
            self._draw_detection(rendered_frame, detection)
        
        return rendered_frame
    
    def _draw_detection(self, frame: np.ndarray, detection: Detection) -> None:
        """Draw a single detection on the frame"""
        x1, y1, x2, y2 = detection.bbox
        color = self.colors.get(detection.class_id, (0, 255, 0))
        
        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, self.line_thickness)
        
        # Prepare label
        label = f"{detection.class_name}: {detection.confidence:.2f}"
        
        # Get label size
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 
                                   self.font_scale, self.line_thickness)[0]
        
        # Draw label background
        cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                     (x1 + label_size[0], y1), color, -1)
        
        # Draw label text
        cv2.putText(frame, label, (x1, y1 - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, 
                   (0, 0, 0), self.line_thickness)
    
    def add_info_overlay(self, frame: np.ndarray, info: Dict[str, Any]) -> np.ndarray:
        """
        Add information overlay to frame
        
        Args:
            frame: Input frame
            info: Dictionary with information to display
            
        Returns:
            Frame with information overlay
        """
        overlay_frame = frame.copy()
        
        y_offset = 20
        for key, value in info.items():
            text = f"{key}: {value}"
            cv2.putText(overlay_frame, text, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, 
                       (0, 255, 0), 1)
            y_offset += 25
        
        return overlay_frame