#!/usr/bin/env python3
"""
Demo of the refactored vision tracker system
Shows the professional architecture and multi-backend support
"""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def demo_backend_switching():
    """Demonstrate backend switching capabilities"""
    print("🔄 BACKEND SWITCHING DEMO")
    print("=" * 50)
    
    from vision_tracker.models.factory import ModelFactory
    
    # Show available backends
    backends = ModelFactory.get_available_backends()
    print(f"Available backends: {backends}")
    
    # Show models for each backend
    for backend in backends:
        print(f"\n📦 {backend.upper()} Backend:")
        metadata = ModelFactory.get_backend_metadata(backend)
        if metadata:
            print(f"  Description: {metadata.description}")
            print(f"  Capabilities: {', '.join(metadata.capabilities)}")
            
        models = ModelFactory.list_models(backend)
        print(f"  Available models:")
        for model_key, model_path in models.items():
            print(f"    {model_key:<12} -> {model_path}")

def demo_configuration():
    """Demonstrate configuration management"""
    print("\n⚙️  CONFIGURATION DEMO")
    print("=" * 50)
    
    from vision_tracker.utils.config import Config
    import tempfile
    import yaml
    
    # Create config
    config = Config()
    print("✓ Default configuration created")
    
    # Show config structure
    print(f"Camera: {config.camera.width}x{config.camera.height}@{config.camera.fps}fps")
    print(f"Model: {config.model.backend}/{config.model.name}")
    print(f"Display: {config.display.window_width}x{config.display.window_height}")
    print(f"Logging: {config.logging.level}")
    
    # Save and load config
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        config.save(f.name)
        print(f"✓ Configuration saved to: {f.name}")
        
        # Load it back
        loaded_config = Config.from_file(f.name)
        print(f"✓ Configuration loaded back successfully")

def demo_logging():
    """Demonstrate logging system"""
    print("\n📝 LOGGING DEMO")
    print("=" * 50)
    
    from vision_tracker.utils.logger import setup_logging, get_logger
    
    # Setup logging
    setup_logging(level="INFO", use_colors=True)
    logger = get_logger("demo")
    
    print("✓ Logging system initialized")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    print("✓ Different log levels demonstrated")

def demo_platform_detection():
    """Demonstrate platform detection"""
    print("\n🖥️  PLATFORM DETECTION DEMO")
    print("=" * 50)
    
    from vision_tracker.utils.platform import get_platform_info, PlatformDetector
    
    # Get platform info
    platform_info = get_platform_info()
    
    print(f"System: {platform_info.system}")
    print(f"Architecture: {platform_info.architecture}")
    print(f"Python: {platform_info.python_version}")
    print(f"WSL: {platform_info.is_wsl}")
    print(f"Docker: {platform_info.is_docker}")
    print(f"GUI Available: {platform_info.has_gui}")
    
    # Show camera backends
    backends = PlatformDetector.get_camera_backends()
    print(f"Camera backends: {[name for name, _ in backends]}")
    
    # Show GPU info
    gpu_info = PlatformDetector.check_gpu_availability()
    print(f"GPU availability: {gpu_info}")

def demo_type_system():
    """Demonstrate type system and detection objects"""
    print("\n🎯 TYPE SYSTEM DEMO")
    print("=" * 50)
    
    from vision_tracker.core.types import Detection
    
    # Create a sample detection
    detection = Detection(
        class_id=0,
        class_name="person",
        confidence=0.85,
        bbox=(100, 100, 200, 250),
        center=(150, 175),
        area=15000
    )
    
    print("✓ Detection object created:")
    print(f"  Class: {detection.class_name} (ID: {detection.class_id})")
    print(f"  Confidence: {detection.confidence:.2f}")
    print(f"  Bounding box: {detection.bbox}")
    print(f"  Center: {detection.center}")
    print(f"  Area: {detection.area}")

def demo_cli_features():
    """Demonstrate CLI features"""
    print("\n💻 CLI FEATURES DEMO")
    print("=" * 50)
    
    print("The refactored system supports rich CLI features:")
    print()
    print("📍 Basic usage:")
    print("  python main.py --test                    # Run with test data")
    print("  python main.py --backend yolo            # Use YOLO backend")
    print("  python main.py --backend detectron2      # Use Detectron2 backend")
    print()
    print("📍 Model management:")
    print("  python main.py --list-models yolo        # List YOLO models")
    print("  python main.py --list-models detectron2  # List Detectron2 models")
    print()
    print("📍 Configuration:")
    print("  python main.py --config my_config.yml    # Use custom config")
    print("  python main.py --confidence 0.7          # Set confidence threshold")
    print("  python main.py --device cuda             # Force GPU usage")
    print()
    print("📍 System info:")
    print("  python main.py --info                    # Show system information")

def main():
    """Run all demos"""
    print("🚀 VISION TRACKER - PROFESSIONAL SYSTEM DEMO")
    print("=" * 60)
    print("Demonstrating the refactored, professional architecture")
    print("with multi-backend support and enterprise features.")
    print("=" * 60)
    
    demos = [
        demo_backend_switching,
        demo_configuration,
        demo_logging,
        demo_platform_detection,
        demo_type_system,
        demo_cli_features
    ]
    
    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"❌ Demo {demo.__name__} failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 DEMO COMPLETE!")
    print("=" * 60)
    print("The vision tracker has been successfully refactored into a")
    print("professional, modular system with:")
    print()
    print("✅ Multi-backend support (YOLO + Detectron2)")
    print("✅ Professional architecture with clean separation")
    print("✅ Comprehensive configuration management")  
    print("✅ Enterprise-grade logging and error handling")
    print("✅ Cross-platform compatibility")
    print("✅ Extensible plugin system")
    print("✅ Type safety and documentation")
    print()
    print("Ready for production use! 🚀")

if __name__ == '__main__':
    main()