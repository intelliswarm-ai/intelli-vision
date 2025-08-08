#!/usr/bin/env python3
"""
Basic test of the refactored vision tracker system
"""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test basic imports"""
    print("Testing basic imports...")
    
    try:
        from vision_tracker.utils.config import Config
        print("✓ Config import successful")
        
        from vision_tracker.utils.logger import get_logger
        print("✓ Logger import successful")
        
        from vision_tracker.utils.platform import get_platform_info
        print("✓ Platform utils import successful")
        
        from vision_tracker.models.factory import ModelFactory
        print("✓ Model factory import successful")
        
        from vision_tracker.core.types import Detection
        print("✓ Detection types import successful")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_config():
    """Test configuration system"""
    print("\nTesting configuration system...")
    
    try:
        from vision_tracker.utils.config import Config
        
        # Test default config creation
        config = Config()
        print(f"✓ Default config created")
        print(f"  Camera backend: {config.camera.backend}")
        print(f"  Model backend: {config.model.backend}")
        print(f"  Display size: {config.display.window_width}x{config.display.window_height}")
        
        return True
    except Exception as e:
        print(f"✗ Config test failed: {e}")
        return False

def test_platform_detection():
    """Test platform detection"""
    print("\nTesting platform detection...")
    
    try:
        from vision_tracker.utils.platform import get_platform_info
        
        platform_info = get_platform_info()
        print(f"✓ Platform info retrieved")
        print(f"  System: {platform_info.system}")
        print(f"  Is WSL: {platform_info.is_wsl}")
        print(f"  Is Docker: {platform_info.is_docker}")
        print(f"  Has GUI: {platform_info.has_gui}")
        
        return True
    except Exception as e:
        print(f"✗ Platform detection failed: {e}")
        return False

def test_model_factory():
    """Test model factory"""
    print("\nTesting model factory...")
    
    try:
        from vision_tracker.models.factory import ModelFactory
        
        # Test backend listing
        backends = ModelFactory.get_available_backends()
        print(f"✓ Available backends: {backends}")
        
        # Test model listing
        for backend in backends:
            models = ModelFactory.list_models(backend)
            print(f"  {backend} models: {list(models.keys())}")
        
        return True
    except Exception as e:
        print(f"✗ Model factory test failed: {e}")
        return False

def test_basic_detector():
    """Test basic detector without loading models"""
    print("\nTesting basic detector setup...")
    
    try:
        from vision_tracker.core.detector import ObjectDetector
        from vision_tracker.utils.config import ModelConfig
        
        # Create detector (don't load model)
        config = ModelConfig()
        detector = ObjectDetector(config)
        print(f"✓ Detector created")
        print(f"  Available backends: {detector.get_available_backends()}")
        
        return True
    except Exception as e:
        print(f"✗ Basic detector test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("VISION TRACKER - BASIC SYSTEM TEST")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_config,
        test_platform_detection,
        test_model_factory,
        test_basic_detector
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 All basic tests passed! The refactored system is working.")
        return 0
    else:
        print("❌ Some tests failed. Check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())