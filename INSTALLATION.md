# Installation Guide - Vision Tracker

## 🚀 Quick Install (Recommended)

### Option 1: Mock Backend (No Dependencies - Works Everywhere)
```bash
# Clone and test immediately
git clone https://github.com/intelliswarm-ai/vision-tracker.git
cd vision-tracker
python main.py --test --backend mock
```

### 🔄 NEW: Dynamic Backend Switching
```bash
# Install both YOLO and Detectron2 for dynamic switching
pip install ultralytics torch torchvision
pip install 'git+https://github.com/facebookresearch/detectron2.git'

# Preload multiple backends for instant switching
python main.py --test --preload-backends yolo detectron2 mock

# Runtime Controls:
# Press 'n' to switch to next backend
# Press 'b' to switch to previous backend  
# Press '1', '2', '3' to switch to specific backends
# Press 'i' to show backend information
```

### Option 2: YOLO Backend (Production Ready)
```bash
# Install YOLO dependencies
pip install ultralytics torch torchvision

# Fix potential conflicts
pip install 'pyparsing>=2.4.0,<4.0.0'

# Test with YOLO
python main.py --test --backend yolo
```

### Option 3: Detectron2 Backend (Advanced)
```bash
# Install PyTorch first
pip install torch torchvision

# Install Detectron2
pip install 'git+https://github.com/facebookresearch/detectron2.git'

# Test with Detectron2
python main.py --test --backend detectron2
```

## 🔧 Platform-Specific Instructions

### Windows (Native)
```batch
# Install Python 3.8+ from python.org
# Then install dependencies:
pip install ultralytics torch torchvision
python main.py --test --backend yolo
```

### Windows (WSL/WSL2)
```bash
# For GUI support, ensure WSLg is enabled (Windows 11)
# Or use headless mode:
python main.py --test --backend mock --no-display

# For camera access, USB passthrough setup required
```

### Linux (Native)
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-pip python3-opencv

# Install Python dependencies
pip3 install ultralytics torch torchvision

# Test
python3 main.py --test --backend yolo
```

### macOS
```bash
# Install via Homebrew
brew install python opencv

# Install dependencies
pip install ultralytics torch torchvision

# Test
python main.py --test --backend yolo
```

## 🐳 Docker Installation

### Quick Docker Test
```bash
# Build and run with mock backend
docker build -t vision-tracker .
docker run -it vision-tracker python main.py --test --backend mock --no-display
```

### Full Docker with GUI
```bash
# Linux: Enable X11 forwarding
xhost +local:docker

# Run with display
docker run -it \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  vision-tracker python main.py --test --backend mock
```

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. "ImportError: cannot import name 'Group' from 'pyparsing'"
```bash
pip uninstall pyparsing
pip install 'pyparsing>=2.4.0,<4.0.0'
```

#### 2. "ImportError: cannot import name 'Cycler' from 'cycler'"
```bash
pip uninstall cycler matplotlib
pip install 'cycler>=0.10.0' 'matplotlib>=3.5.0,<3.8.0'
```

#### 3. "YOLO/Detectron2 not available"
Use the mock backend for testing:
```bash
python main.py --test --backend mock
```

#### 4. "GUI/Display issues in WSL"
Use headless mode:
```bash
python main.py --test --backend mock --no-display --save-frames
```

#### 5. "Camera not found"
Always works in test mode:
```bash
python main.py --test --backend mock
```

## 📦 Dependency Details

### Core Dependencies (Required)
```bash
# Always required
pip install opencv-python numpy pyyaml
```

### YOLO Backend
```bash
pip install ultralytics torch torchvision
```

### Detectron2 Backend (Linux/macOS recommended)
```bash
# Install PyTorch first
pip install torch torchvision

# Install Detectron2 (can be complex on Windows)
pip install 'git+https://github.com/facebookresearch/detectron2.git'

# Alternative methods:
# conda install detectron2 -c detectron2
# Or build from source (see Detectron2 docs)
```

### Development Dependencies (Optional)
```bash
pip install pytest black flake8 mypy pre-commit
```

## 🎯 Verification

### Test All Features
```bash
# Show system info
python main.py --info

# List available backends
python main.py --list-models yolo
python main.py --list-models detectron2
python main.py --list-models mock

# Test different backends
python main.py --test --backend mock      # Always works
python main.py --test --backend yolo      # If YOLO installed
python main.py --test --backend detectron2 # If Detectron2 installed

# 🔥 NEW: Test dynamic backend switching
python main.py --test --preload-backends yolo detectron2 mock

# Test with real camera (if available)
python main.py --backend mock

# Test headless mode
python main.py --test --backend mock --no-display --save-frames

# Run demo scripts
python demo_backend_switching.py
python test_backend_switching.py
```

## 🚀 Production Deployment

### Server Environment (Headless)
```bash
# Install minimal dependencies
pip install opencv-python-headless ultralytics

# Run headless
python main.py --test --backend yolo --no-display --save-frames --output-dir /path/to/output
```

### GPU Environment
```bash
# Install CUDA-enabled PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Verify GPU usage
python main.py --test --backend yolo --device cuda
```

## 💡 Tips for Success

1. **Start with Mock Backend**: Test the architecture first
2. **Use Virtual Environments**: Avoid dependency conflicts
3. **Check System Requirements**: Ensure Python 3.8+
4. **Read Error Messages**: The system provides helpful guidance
5. **Use Headless Mode**: For servers or environments without GUI
6. **Test Incrementally**: Verify each component works before full deployment

## 📞 Getting Help

If you encounter issues:
1. Check the error message - they're designed to be helpful
2. Try `python main.py --info` to see system status
3. Start with `python main.py --test --backend mock` 
4. Check this troubleshooting guide
5. Create an issue with full error output

The vision tracker is designed to work in most environments with graceful degradation!