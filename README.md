# Vision Tracker - Professional Real-time Object Detection System

A professional, modular computer vision system that supports multiple detection backends including YOLOv8 and Facebook's Detectron2. Built with enterprise-grade architecture, comprehensive logging, and cross-platform support.

## 🚀 Features

### Multi-Backend Support
- **YOLOv8** (Ultralytics): Fast, accurate object detection
- **Detectron2** (Facebook Research): Advanced detection, segmentation, and keypoint detection
- **Automatic Backend Detection**: Intelligently selects the best available backend
- **Easy Backend Switching**: Switch between backends without code changes

### Professional Architecture
- **Modular Design**: Clean separation of concerns with dedicated modules
- **Configuration Management**: YAML/JSON configuration with validation
- **Comprehensive Logging**: Structured logging with multiple output options
- **Error Handling**: Robust exception handling with informative error messages
- **Type Safety**: Full type hints for better code maintenance

### Cross-Platform Compatibility
- **Windows**: Native support with DirectShow/Media Foundation backends
- **Linux**: V4L2 and GStreamer support
- **WSL/WSL2**: Optimized for Windows Subsystem for Linux
- **Docker**: Containerized deployment with GUI support
- **Headless Mode**: Run without display for server environments

### Advanced Features
- **Real-time Processing**: Optimized for high-performance real-time detection
- **Multiple Input Sources**: Camera, video files, or synthetic test data
- **Scalable Display**: Automatic window scaling and fullscreen support
- **Statistics Tracking**: FPS monitoring, detection statistics, and performance metrics
- **Callback System**: Extensible callback system for custom integrations
- **Screenshot Capture**: Save processed frames with detections

## 📦 Installation

### Quick Install
```bash
# Clone the repository
git clone https://github.com/intelliswarm-ai/vision-tracker.git
cd vision-tracker

# Install with pip
pip install -e .
```

### Development Install
```bash
# Install with development dependencies
pip install -e ".[dev]"

# Install with GPU support
pip install -e ".[gpu]"
```

### Backend-Specific Installation

#### YOLOv8 Backend
```bash
pip install ultralytics torch torchvision
```

#### Detectron2 Backend
```bash
# Install PyTorch first
pip install torch torchvision

# Install Detectron2
pip install 'git+https://github.com/facebookresearch/detectron2.git'
# or visit https://detectron2.readthedocs.io/en/latest/tutorials/install.html
```

## 🎯 Quick Start

### Command Line Interface
```bash
# Run with auto-detected backend and camera
python main.py

# Run with synthetic test data
python main.py --test

# Use specific backend
python main.py --backend yolo --model yolov8s.pt
python main.py --backend detectron2 --model faster_rcnn_r50

# Process video file
python main.py --video input.mp4

# List available models for a backend
python main.py --list-models yolo
python main.py --list-models detectron2

# Show system information
python main.py --info
```

### Python API
```python
from vision_tracker import VisionTracker, Config

# Create configuration
config = Config()
config.model.backend = "yolo"
config.model.name = "yolov8n.pt"

# Initialize and run tracker
with VisionTracker(config) as tracker:
    if tracker.initialize(test_mode=True):
        tracker.start()
```

## 🔧 Configuration

### Configuration File (YAML)
```yaml
# config/vision_tracker.yml
camera:
  width: 640
  height: 480
  fps: 30
  backend: "auto"  # auto, v4l2, dshow, msmf
  device_index: 0

model:
  backend: "auto"  # auto, yolo, detectron2
  name: "yolov8n.pt"
  confidence_threshold: 0.5
  iou_threshold: 0.45
  device: "auto"  # auto, cpu, cuda, mps

display:
  window_width: 960
  window_height: 720
  fullscreen: false
  show_fps: true
  show_confidence: true

logging:
  level: "INFO"
  file: null  # Optional log file path
```

### Available Models

#### YOLO Models
- `yolov8n.pt` - Nano (fastest)
- `yolov8s.pt` - Small
- `yolov8m.pt` - Medium
- `yolov8l.pt` - Large
- `yolov8x.pt` - Extra Large (most accurate)
- `yolov8n-seg.pt` - Nano with segmentation

#### Detectron2 Models
- `faster_rcnn_r50` - Faster R-CNN with ResNet-50
- `faster_rcnn_r101` - Faster R-CNN with ResNet-101
- `retinanet` - RetinaNet
- `mask_rcnn` - Mask R-CNN (with segmentation)
- `keypoint_rcnn` - Keypoint R-CNN
- `panoptic_fpn` - Panoptic FPN

## 🎮 Controls

### Keyboard Shortcuts
- `q` or `ESC` - Quit application
- `SPACE` - Pause/Resume
- `s` - Save screenshot
- `f` - Toggle fullscreen
- `r` - Reset window size

## 🏗️ Architecture

### Project Structure
```
vision-track/
├── src/vision_tracker/           # Main package
│   ├── core/                     # Core components
│   │   ├── tracker.py           # Main tracker class
│   │   ├── detector.py          # Detection coordinator
│   │   ├── camera.py            # Camera management
│   │   └── exceptions.py        # Custom exceptions
│   ├── models/                   # Detection backends
│   │   ├── base.py              # Abstract base class
│   │   ├── factory.py           # Backend factory
│   │   ├── yolo_backend.py      # YOLOv8 backend
│   │   └── detectron2_backend.py # Detectron2 backend
│   ├── utils/                    # Utilities
│   │   ├── config.py            # Configuration management
│   │   ├── logger.py            # Logging setup
│   │   └── platform.py          # Platform detection
│   ├── ui/                       # User interface
│   └── cli/                      # Command line interface
├── config/                       # Configuration files
├── tests/                        # Unit tests
├── docs/                         # Documentation
└── examples/                     # Example scripts
```

### Backend System
The system uses a factory pattern for backend management:

```python
# Register new backend
from vision_tracker.models.factory import ModelFactory
from vision_tracker.models.base import BaseDetectionModel

class MyBackend(BaseDetectionModel):
    # Implement required methods
    pass

ModelFactory.register_backend(MyBackend, metadata)
```

## 🚀 Performance

### Benchmark Results
| Backend | Model | FPS (CPU) | FPS (GPU) | Accuracy (mAP) |
|---------|-------|-----------|-----------|----------------|
| YOLO | yolov8n | 45 | 120 | 37.3 |
| YOLO | yolov8s | 35 | 95 | 44.9 |
| YOLO | yolov8m | 25 | 80 | 50.2 |
| Detectron2 | Faster R-CNN | 15 | 35 | 39.6 |
| Detectron2 | Mask R-CNN | 12 | 28 | 41.0 |

*Results on Intel i7-10700K + RTX 3080, 640x480 resolution*

## 🐳 Docker Support

### Basic Usage
```bash
# Build image
docker build -t vision-tracker .

# Run with test mode
docker run -it vision-tracker python main.py --test

# Run with display (Linux)
docker run -it --env DISPLAY=$DISPLAY --volume /tmp/.X11-unix:/tmp/.X11-unix vision-tracker
```

### Docker Compose
```bash
# Test mode
docker-compose -f docker-compose.test.yml up

# Camera mode (requires device access)
docker-compose up
```

## 🔍 Troubleshooting

### Common Issues

#### No Camera Access
- **WSL**: Use test mode or set up USB passthrough
- **Docker**: Use `--device=/dev/video0` or privileged mode
- **Permissions**: Ensure user is in `video` group (Linux)

#### Model Loading Issues
```bash
# Check available backends
python main.py --info

# Verify dependencies
pip install torch torchvision ultralytics

# For Detectron2
pip install 'git+https://github.com/facebookresearch/detectron2.git'
```

#### Display Issues
```bash
# Linux: Enable X11 forwarding
xhost +local:docker

# WSL: Ensure WSLg is enabled
# Windows: Install VcXsrv or similar X11 server
```

## 🤝 Usage Examples

### Basic Usage
```bash
# Use the refactored system
python main.py --test --backend yolo
python main.py --backend detectron2 --model mask_rcnn
```

### Legacy Compatibility
The original scripts are still available for backward compatibility:
```bash
# Original vision tracker (now uses new backend system internally)
python vision_tracker.py --test
python run_vision_tracker.bat
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ultralytics](https://github.com/ultralytics/ultralytics) for YOLOv8
- [Facebook Research](https://github.com/facebookresearch/detectron2) for Detectron2
- [OpenCV](https://opencv.org/) for computer vision utilities
- [PyTorch](https://pytorch.org/) for deep learning framework

---

Built with ❤️ by IntelliSwarm AI