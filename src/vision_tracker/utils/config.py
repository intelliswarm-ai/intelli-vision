"""
Configuration Management Module

Handles configuration loading, validation, and management for the Vision Tracker system.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict

from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class CameraConfig:
    """Camera configuration settings"""
    width: int = 640
    height: int = 480
    fps: int = 30
    backend: str = "auto"  # auto, v4l2, dshow, msmf
    device_index: int = 0


@dataclass
class ModelConfig:
    """Model configuration settings"""
    backend: str = "auto"  # auto, yolo, detectron2
    name: str = "yolov8n.pt"
    confidence_threshold: float = 0.5
    iou_threshold: float = 0.45
    device: str = "auto"  # auto, cpu, cuda, mps
    cache_dir: Optional[str] = None


@dataclass
class DisplayConfig:
    """Display configuration settings"""
    window_width: int = 960
    window_height: int = 720
    fullscreen: bool = False
    show_fps: bool = True
    show_confidence: bool = True
    font_scale: float = 0.6
    line_thickness: int = 2


@dataclass
class LoggingConfig:
    """Logging configuration settings"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None
    max_file_size: int = 10_000_000  # 10MB
    backup_count: int = 5


@dataclass
class Config:
    """Main configuration class"""
    camera: CameraConfig = None
    model: ModelConfig = None
    display: DisplayConfig = None
    logging: LoggingConfig = None
    
    def __post_init__(self):
        """Initialize default values after dataclass creation"""
        if self.camera is None:
            self.camera = CameraConfig()
        if self.model is None:
            self.model = ModelConfig()
        if self.display is None:
            self.display = DisplayConfig()
        if self.logging is None:
            self.logging = LoggingConfig()
    
    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> 'Config':
        """Load configuration from file"""
        config_path = Path(config_path)
        
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}. Using defaults.")
            return cls()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yml', '.yaml']:
                    data = yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    data = json.load(f)
                else:
                    raise ValueError(f"Unsupported config format: {config_path.suffix}")
            
            logger.info(f"Loaded configuration from: {config_path}")
            return cls.from_dict(data)
            
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            logger.info("Using default configuration")
            return cls()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Create configuration from dictionary"""
        config = cls()
        
        # Update camera config
        if 'camera' in data:
            camera_data = data['camera']
            config.camera = CameraConfig(**{
                k: v for k, v in camera_data.items() 
                if k in CameraConfig.__dataclass_fields__
            })
        
        # Update model config
        if 'model' in data:
            model_data = data['model']
            config.model = ModelConfig(**{
                k: v for k, v in model_data.items() 
                if k in ModelConfig.__dataclass_fields__
            })
        
        # Update display config
        if 'display' in data:
            display_data = data['display']
            config.display = DisplayConfig(**{
                k: v for k, v in display_data.items() 
                if k in DisplayConfig.__dataclass_fields__
            })
        
        # Update logging config
        if 'logging' in data:
            logging_data = data['logging']
            config.logging = LoggingConfig(**{
                k: v for k, v in logging_data.items() 
                if k in LoggingConfig.__dataclass_fields__
            })
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'camera': asdict(self.camera),
            'model': asdict(self.model),
            'display': asdict(self.display),
            'logging': asdict(self.logging)
        }
    
    def save(self, config_path: Union[str, Path]) -> None:
        """Save configuration to file"""
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yml', '.yaml']:
                    yaml.safe_dump(self.to_dict(), f, default_flow_style=False, indent=2)
                elif config_path.suffix.lower() == '.json':
                    json.dump(self.to_dict(), f, indent=2)
                else:
                    raise ValueError(f"Unsupported config format: {config_path.suffix}")
            
            logger.info(f"Configuration saved to: {config_path}")
            
        except Exception as e:
            logger.error(f"Failed to save config to {config_path}: {e}")
            raise
    
    def validate(self) -> bool:
        """Validate configuration settings"""
        try:
            # Validate camera settings
            if self.camera.width <= 0 or self.camera.height <= 0:
                raise ValueError("Camera dimensions must be positive")
            
            if self.camera.fps <= 0:
                raise ValueError("Camera FPS must be positive")
            
            # Validate model settings
            if not (0.0 <= self.model.confidence_threshold <= 1.0):
                raise ValueError("Confidence threshold must be between 0.0 and 1.0")
            
            if not (0.0 <= self.model.iou_threshold <= 1.0):
                raise ValueError("IoU threshold must be between 0.0 and 1.0")
            
            # Validate display settings
            if self.display.window_width <= 0 or self.display.window_height <= 0:
                raise ValueError("Display dimensions must be positive")
            
            if self.display.font_scale <= 0:
                raise ValueError("Font scale must be positive")
            
            if self.display.line_thickness <= 0:
                raise ValueError("Line thickness must be positive")
            
            logger.debug("Configuration validation passed")
            return True
            
        except ValueError as e:
            logger.error(f"Configuration validation failed: {e}")
            return False


def get_default_config_path() -> Path:
    """Get the default configuration file path"""
    return Path("config/vision_tracker.yml")


def load_config(config_path: Optional[Union[str, Path]] = None) -> Config:
    """Load configuration with fallback to defaults"""
    if config_path is None:
        config_path = get_default_config_path()
    
    config = Config.from_file(config_path)
    
    if not config.validate():
        logger.warning("Using default configuration due to validation errors")
        return Config()
    
    return config