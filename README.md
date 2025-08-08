# Vision Track - Real-time Object Detection

A cross-platform Python application that performs real-time object detection using your computer's camera with YOLOv8 and OpenCV.

## Features

- Real-time object detection from webcam feed
- Bounding boxes around detected objects
- Object labels with confidence scores
- Support for 80+ object classes (COCO dataset)
- Cross-platform support (Windows, Linux, WSL)
- Automatic platform detection and configuration
- Test mode when no camera is available

## Quick Start

### Universal Method (All Platforms)

```bash
# Run the universal launcher
python run.py
# or
python3 run.py
```

This will automatically detect your platform and set up the appropriate configuration.

## Platform-Specific Instructions

### Windows (Native)

```batch
# Use the Windows batch file
run_windows.bat

# Or manually:
pip install -r requirements.txt
python vision_tracker.py
```

### Linux

```bash
# Use the Linux script
./run_linux.sh

# Or manually:
pip3 install -r requirements.txt
python3 vision_tracker.py
```

### WSL (Windows Subsystem for Linux)

WSL requires USB passthrough for camera access:

1. **Setup USB passthrough** (one-time setup):
```bash
# Run the setup script for instructions
./setup-wsl-camera.sh
```

2. **Run the application**:
```bash
./run_linux.sh
# Or use Docker (recommended for WSL)
docker-compose up
```

**Note**: Without USB passthrough setup, the app will run in test mode with generated frames.

### Option 2: Run with Docker

1. Allow X11 forwarding (Linux/Mac):
```bash
xhost +local:docker
```

2. Build and run with Docker Compose:
```bash
docker compose up --build
```

Or build and run manually:
```bash
# Build the image
docker build -t vision-tracker .

# Run the container (Linux/Mac)
docker run -it --rm \
  --device=/dev/video0 \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v $(pwd)/models:/root/.cache/ultralytics \
  --network=host \
  vision-tracker
```

### Windows Docker Setup

For Windows with WSL2:
```bash
# Install VcXsrv or another X server
# Launch XLaunch with "Disable access control" checked
# In WSL2, set:
export DISPLAY=host.docker.internal:0

# Then run:
docker compose up --build
```

## Usage

- The application will automatically detect and download the YOLOv8 nano model on first run
- Press 'q' to quit the application
- Objects are detected with confidence threshold of 50%

## Requirements

### Local Installation
- Python 3.7+
- Webcam/camera connected to your computer
- OpenCV
- Ultralytics YOLOv8

### Docker Installation
- Docker and Docker Compose
- Webcam/camera connected to your computer
- X11 server (for GUI display)
  - Linux: Usually pre-installed
  - Mac: XQuartz
  - Windows: VcXsrv or Xming

## Troubleshooting

- **Camera not detected**: Ensure `/dev/video0` exists and has proper permissions
- **Display issues**: Check X11 forwarding is enabled with `xhost +local:docker`
- **Model download**: First run downloads YOLOv8 model (~6MB), stored in `models/` directory"# intelli-vision" 
