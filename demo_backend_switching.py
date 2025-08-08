#!/usr/bin/env python3
"""
Dynamic Backend Switching Demo

Demonstrates the new capability to switch between YOLO and Detectron2 
backends dynamically during runtime.
"""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def demo_available_backends():
    """Show available backends and their capabilities"""
    print("🔍 CHECKING AVAILABLE BACKENDS")
    print("=" * 50)
    
    from vision_tracker.models.factory import ModelFactory
    
    backends = ModelFactory.get_available_backends()
    print(f"Available backends: {backends}")
    
    for backend in backends:
        metadata = ModelFactory.get_backend_metadata(backend)
        if metadata:
            print(f"\n📦 {backend.upper()} Backend:")
            print(f"  Description: {metadata.description}")
            print(f"  Capabilities: {', '.join(metadata.capabilities)}")
            print(f"  Requirements: {metadata.requirements}")
            
            # Check if dependencies are available
            missing_deps = ModelFactory._check_requirements(metadata)
            if missing_deps:
                print(f"  Status: ❌ Missing dependencies: {missing_deps}")
                print(f"  Install: pip install {' '.join(missing_deps)}")
            else:
                print(f"  Status: ✅ Ready to use")

def demo_cli_usage():
    """Show CLI usage examples"""
    print("\n💻 DYNAMIC BACKEND SWITCHING - CLI USAGE")
    print("=" * 50)
    
    print("🎯 Basic Usage Examples:")
    print()
    print("1. Test with mock backend (no dependencies):")
    print("   python main.py --test --backend mock")
    print()
    print("2. Run with YOLO backend:")
    print("   python main.py --test --backend yolo")
    print()
    print("3. Run with Detectron2 backend:")
    print("   python main.py --test --backend detectron2")
    print()
    print("🚀 DYNAMIC SWITCHING - Preload Multiple Backends:")
    print()
    print("4. Preload YOLO + Detectron2 for instant switching:")
    print("   python main.py --test --preload-backends yolo detectron2")
    print()
    print("5. Preload all available backends:")
    print("   python main.py --test --preload-backends yolo detectron2 mock")
    print()
    print("⌨️  Runtime Controls (when multiple backends loaded):")
    print("   'n'     - Switch to next backend")
    print("   'b'     - Switch to previous backend") 
    print("   '1'     - Switch to first backend")
    print("   '2'     - Switch to second backend")
    print("   '3'     - Switch to third backend")
    print("   'i'     - Show backend information")
    print("   'q'     - Quit")

def demo_python_api():
    """Demonstrate Python API usage"""
    print("\n🐍 PYTHON API - DYNAMIC SWITCHING")
    print("=" * 50)
    
    print("""
from vision_tracker.core.tracker import VisionTracker
from vision_tracker.utils.config import Config

# Create configuration
config = Config()

# Initialize tracker
tracker = VisionTracker(config)

# Initialize with multiple backends
backends = ['yolo', 'detectron2', 'mock']
tracker.initialize(test_mode=True, preload_backends=backends)

# Check available backends
print("Available:", tracker.get_available_backends())
print("Current:", tracker.get_current_backend())

# Switch backends programmatically
tracker.switch_backend_by_name('detectron2')
print("Switched to:", tracker.get_current_backend())

tracker.switch_backend_by_name('yolo')
print("Switched to:", tracker.get_current_backend())

# Start tracking (will use current backend)
tracker.start()
""")

def demo_features():
    """List all new features"""
    print("\n✨ NEW FEATURES - DYNAMIC BACKEND SWITCHING")
    print("=" * 50)
    
    features = [
        "🔄 Runtime backend switching without restart",
        "⚡ Instant switching with preloaded models",
        "🎮 Keyboard shortcuts for quick switching",
        "📊 On-screen display of current backend",
        "🛡️ Graceful fallback if backend fails",
        "📝 Detailed backend information display",
        "🔍 Auto-detection of available backends",
        "⚙️ CLI and Python API support",
        "🎯 Support for YOLO + Detectron2 + Mock",
        "💾 Memory efficient backend management"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print("\n🎯 USE CASES:")
    print("  • Compare model performance in real-time")
    print("  • Switch between speed vs accuracy models")
    print("  • Demo different detection capabilities")
    print("  • Development and testing workflows")
    print("  • Educational and research applications")

def demo_installation_check():
    """Check what backends can be used"""
    print("\n🔧 INSTALLATION CHECK")
    print("=" * 50)
    
    try:
        from vision_tracker.models.factory import ModelFactory
        
        # Check each backend
        backends_to_check = ['yolo', 'detectron2', 'mock']
        ready_backends = []
        
        for backend in backends_to_check:
            metadata = ModelFactory.get_backend_metadata(backend)
            if metadata:
                missing_deps = ModelFactory._check_requirements(metadata)
                if not missing_deps:
                    ready_backends.append(backend)
                    print(f"✅ {backend.upper()}: Ready")
                else:
                    print(f"❌ {backend.upper()}: Missing {missing_deps}")
                    print(f"   Install: pip install {' '.join(missing_deps)}")
            else:
                print(f"❓ {backend.upper()}: Not registered")
        
        print(f"\n🎯 Ready for dynamic switching: {len(ready_backends)} backends")
        
        if len(ready_backends) >= 2:
            print("🚀 You can use dynamic backend switching!")
            print(f"   Try: python main.py --test --preload-backends {' '.join(ready_backends)}")
        elif len(ready_backends) == 1:
            print(f"📝 Only {ready_backends[0]} available - install more for switching")
        else:
            print("⚠️  No backends ready - check installation")
            
    except Exception as e:
        print(f"Error checking backends: {e}")

def main():
    """Main demo function"""
    print("🔄 VISION TRACKER - DYNAMIC BACKEND SWITCHING DEMO")
    print("=" * 60)
    print("This demo showcases the new capability to switch between")
    print("different detection backends (YOLO, Detectron2) dynamically")
    print("during runtime without restarting the application.")
    print("=" * 60)
    
    demo_installation_check()
    demo_available_backends()
    demo_features()
    demo_cli_usage()
    demo_python_api()
    
    print("\n" + "=" * 60)
    print("🎉 READY FOR DYNAMIC BACKEND SWITCHING!")
    print("=" * 60)
    print("You can now switch between YOLO and Detectron2 backends")
    print("in real-time while the application is running.")
    print()
    print("🚀 Quick Start:")
    print("   python main.py --test --preload-backends yolo detectron2 mock")
    print()
    print("Then press 'n' to switch backends while running!")
    print("=" * 60)

if __name__ == '__main__':
    main()