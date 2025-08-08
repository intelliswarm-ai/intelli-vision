# 🔄 Dynamic Backend Switching - Vision Tracker

A professional real-time object detection system with **dynamic backend switching** capability. Switch between YOLO, Detectron2, and Mock backends instantly during runtime without restarting the application.

## ✨ New Features

### 🚀 Dynamic Backend Switching
- **Runtime Switching**: Change detection models instantly while running
- **Preloaded Backends**: Load multiple models at startup for instant switching
- **Keyboard Controls**: Press hotkeys to switch between backends
- **Performance Comparison**: Compare model performance in real-time
- **Graceful Fallback**: Automatic fallback if a backend fails

### 🎮 Interactive Controls
- `n` - Switch to next backend
- `b` - Switch to previous backend  
- `1`, `2`, `3` - Switch to specific backend by number
- `i` - Show detailed backend information
- `q` / `ESC` - Quit application

### 📊 On-Screen Display
- Current backend name displayed in real-time
- Backend switching indicator (1/3, 2/3, etc.)
- Performance metrics per backend
- Detection statistics

## 🏃‍♂️ Quick Start

### 1. Install Dependencies (Optional - Mock works without any)
```bash
# For YOLO support
pip install ultralytics torch torchvision

# For Detectron2 support (Linux/macOS recommended)
pip install torch torchvision
pip install 'git+https://github.com/facebookresearch/detectron2.git'
```

### 2. Run with Dynamic Switching
```bash
# Preload multiple backends for instant switching
python main.py --test --preload-backends yolo detectron2 mock

# Or start with mock (works everywhere) and see the architecture
python main.py --test --preload-backends mock
```

### 3. Switch Backends While Running
Once running, use these controls:
- Press `n` to cycle through backends
- Press `1`, `2`, `3` to jump to specific backends
- Press `i` to see backend details
- Watch the on-screen display update!

## 🔧 Usage Examples

### CLI Usage
```bash
# Single backend (traditional)
python main.py --test --backend yolo

# Dynamic switching with 2 backends
python main.py --test --preload-backends yolo detectron2

# All three backends + real camera
python main.py --camera 0 --preload-backends yolo detectron2 mock

# Headless mode with switching
python main.py --test --preload-backends yolo mock --no-display
```

### Python API
```python
from vision_tracker.core.tracker import VisionTracker
from vision_tracker.utils.config import Config

# Initialize with multiple backends
config = Config()
tracker = VisionTracker(config)
tracker.initialize(test_mode=True, preload_backends=['yolo', 'detectron2', 'mock'])

# Check what's available
print("Available:", tracker.get_available_backends())
print("Current:", tracker.get_current_backend())

# Switch programmatically
tracker.switch_backend_by_name('detectron2')
print("Now using:", tracker.get_current_backend())

# Start with current backend
tracker.start()
```

## 🏗️ Architecture

### Backend System
```
ModelFactory
├── YOLOBackend      (ultralytics)
├── Detectron2Backend (detectron2)  
└── MockBackend      (no dependencies)

VisionTracker
├── preloaded_backends: Dict[str, ObjectDetector]
├── current_backend_index: int
└── backend_switching_enabled: bool
```

### Switching Process
1. **Preload Phase**: Load all specified backends at initialization
2. **Runtime Switching**: Change `self.detector` pointer instantly
3. **State Preservation**: Keep camera, display, and stats intact
4. **Performance Tracking**: Track metrics per backend

## 📈 Performance Comparison

| Backend | Speed | Accuracy | Memory | Use Case |
|---------|-------|----------|--------|----------|
| **Mock** | ⚡⚡⚡ | N/A | 🔋 | Testing, Demo |
| **YOLO** | ⚡⚡ | ⭐⭐⭐ | 🔋🔋 | Real-time, Speed |
| **Detectron2** | ⚡ | ⭐⭐⭐⭐ | 🔋🔋🔋 | Accuracy, Research |

Switch between them instantly to find the best trade-off for your use case!

## 🎯 Use Cases

### 🔬 Research & Development
- Compare model performance side-by-side
- Test different detection approaches
- Rapid prototyping with multiple models

### 🎓 Education & Training
- Demonstrate different CV techniques
- Teaching model trade-offs
- Interactive ML demonstrations

### 🚀 Production Testing
- A/B test different models
- Performance benchmarking
- Quality assurance testing

### 🎮 Demonstrations
- Live demos with multiple models
- Conference presentations
- Customer showcases

## 📊 System Information

```bash
# Check what backends are available
python main.py --info

# List models for each backend
python main.py --list-models yolo
python main.py --list-models detectron2
python main.py --list-models mock

# Test backend functionality
python test_backend_switching.py

# See switching demo
python demo_backend_switching.py
```

## 🔍 Technical Details

### Memory Management
- Backends are loaded once and cached
- Switching changes only the active detector pointer
- Efficient memory usage with shared resources

### Error Handling
- Graceful degradation if backends fail to load
- Automatic fallback to available backends
- Detailed error messages with installation help

### Thread Safety
- Backend switching is thread-safe
- No race conditions during switching
- Consistent state management

## 🐛 Troubleshooting

### Backend Not Loading
```bash
# Check what's missing
python main.py --info

# Install missing dependencies
pip install ultralytics  # For YOLO
pip install detectron2   # For Detectron2
```

### Switching Not Working
- Ensure multiple backends in `--preload-backends`
- Check that backends loaded successfully in logs
- Verify keyboard input is being captured (GUI mode)

### Performance Issues
- Start with mock backend for testing
- Use `--no-display` for headless performance
- Monitor per-backend metrics with `i` key

## 🤝 Contributing

This dynamic switching system makes the vision tracker highly extensible:

1. **Add New Backends**: Implement `BaseDetectionModel` interface
2. **Custom Switching Logic**: Override switching methods
3. **Performance Metrics**: Add custom performance tracking
4. **UI Enhancements**: Extend on-screen displays

## 📄 License

Same license as the main Vision Tracker project.

---

## 🎉 Summary

**Dynamic Backend Switching** transforms the Vision Tracker from a single-model system into a flexible, multi-model platform. Switch between YOLO's speed, Detectron2's accuracy, and Mock's convenience - all in real-time, all in one application.

Perfect for research, education, development, and production testing!

```bash
# Try it now!
python main.py --test --preload-backends yolo detectron2 mock
# Then press 'n' to switch backends while running!
```