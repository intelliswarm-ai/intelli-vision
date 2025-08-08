# Vision Tracker - Docker Usage Guide

## Overview
The Vision Tracker has been updated to handle Docker environments gracefully. It now supports multiple input modes and provides fallback options when camera access is not available.

## Running Modes

### 1. Test Mode (Synthetic Data)
Runs with computer-generated test frames. No camera required.

```bash
# Using docker-compose
docker-compose -f docker-compose.test.yml up

# Or directly with docker
docker run -it vision-tracker --test
```

### 2. Video File Mode
Process a pre-recorded video file.

```bash
# Using docker-compose
docker-compose -f docker-compose.video.yml up

# Or with custom video
docker run -it -v $(pwd)/videos:/app/videos vision-tracker python vision_tracker.py --source /app/videos/your_video.mp4
```

### 3. Camera Mode (When Available)
Use a real camera device.

```bash
# Standard docker-compose (attempts camera access)
docker-compose up

# With specific device
docker run -it --device=/dev/video0 vision-tracker

# With privileged mode (access all devices)
docker run -it --privileged vision-tracker
```

## Features

### Command Line Arguments
- `--test`: Run in test mode with synthetic data
- `--source <path_or_index>`: Specify video source (file path or camera index)
- `--model <path>`: Specify YOLO model file (default: yolov8n.pt)

### Controls
- **'q'**: Quit the application
- **'s'**: Save a screenshot

### Display Modes
The tracker shows:
- Real-time object detection boxes
- Class labels and confidence scores
- FPS counter
- Timestamp (in test mode)

## Troubleshooting

### No Camera Access in Docker
This is expected behavior. Docker containers have limited hardware access by default. Solutions:

1. **Use Test Mode**: Recommended for testing and development
   ```bash
   docker-compose -f docker-compose.test.yml up
   ```

2. **Use Video Files**: Process pre-recorded videos
   ```bash
   python generate_sample_video.py  # Generate a test video
   docker run -it -v $(pwd):/app/data vision-tracker python vision_tracker.py --source /app/data/sample_video.mp4
   ```

3. **Enable Camera Access** (Linux only):
   ```bash
   # Grant device access
   docker run -it --device=/dev/video0 vision-tracker
   
   # Or use privileged mode
   docker run -it --privileged vision-tracker
   ```

### WSL2 Camera Issues
WSL2 doesn't support USB passthrough by default. Options:
- Use WSLg with USB/IP tools
- Run in test mode
- Use Windows native or a Linux VM

### X11 Display Issues
If you get display errors:

```bash
# Linux
xhost +local:docker

# Windows with WSL2
export DISPLAY=:0

# macOS
# Install XQuartz and enable connections from network clients
```

## Generate Test Data

Create a sample video for testing:

```bash
python generate_sample_video.py --duration 60 --fps 30 --output test_video.mp4
```

## Performance Notes

- Test mode runs at ~30 FPS (simulated)
- Real detection performance depends on:
  - Model size (yolov8n is fastest, yolov8x is most accurate)
  - Hardware (GPU acceleration if available)
  - Input resolution

## Development

To modify and rebuild:

```bash
# Edit vision_tracker.py or other files
# Rebuild the Docker image
docker-compose build

# Run with new changes
docker-compose up
```