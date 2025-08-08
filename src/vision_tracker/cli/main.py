"""
Main CLI Application

Professional command-line interface for the Vision Tracker system.
"""

import argparse
import sys
import signal
from pathlib import Path
from typing import Optional

from ..utils.logger import setup_logging, get_logger
from ..utils.config import Config, load_config
from ..utils.platform import get_platform_info
from ..core.tracker import VisionTracker, TrackerState
from ..core.exceptions import VisionTrackerError


class VisionTrackerCLI:
    """
    Command Line Interface for Vision Tracker
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.tracker: Optional[VisionTracker] = None
        self.config: Optional[Config] = None
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        if self.tracker:
            self.tracker.stop()
        sys.exit(0)
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser"""
        parser = argparse.ArgumentParser(
            prog='vision-tracker',
            description='Professional Real-time Object Detection and Tracking System',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  vision-tracker --test                    # Run with synthetic test data
  vision-tracker --camera 0               # Use camera at index 0
  vision-tracker --video input.mp4        # Process video file
  vision-tracker --config my_config.yml   # Use custom configuration
  
For more information, visit: https://github.com/your-org/vision-tracker
            """
        )
        
        # Source options (mutually exclusive)
        source_group = parser.add_mutually_exclusive_group()
        source_group.add_argument(
            '--test', 
            action='store_true',
            help='Run in test mode with synthetic data'
        )
        source_group.add_argument(
            '--camera', 
            type=int, 
            metavar='INDEX',
            help='Use camera at specified index (default: 0)'
        )
        source_group.add_argument(
            '--video', 
            type=str, 
            metavar='PATH',
            help='Process video file'
        )
        
        # Model options
        parser.add_argument(
            '--backend', 
            type=str, 
            choices=['auto', 'yolo', 'detectron2', 'mock'],
            help='Detection backend to use (default: auto)'
        )
        parser.add_argument(
            '--preload-backends',
            type=str,
            nargs='+',
            metavar='BACKEND',
            help='Preload multiple backends for dynamic switching (e.g., --preload-backends yolo detectron2)'
        )
        parser.add_argument(
            '--model', 
            type=str, 
            metavar='PATH',
            help='Model file or identifier (default depends on backend)'
        )
        parser.add_argument(
            '--list-models', 
            type=str, 
            metavar='BACKEND',
            help='List available models for a backend'
        )
        
        # Configuration
        parser.add_argument(
            '--config', 
            type=str, 
            metavar='PATH',
            help='Configuration file path'
        )
        
        # Logging options
        parser.add_argument(
            '--log-level', 
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            default='INFO',
            help='Set logging level (default: INFO)'
        )
        parser.add_argument(
            '--log-file', 
            type=str, 
            metavar='PATH',
            help='Log to file'
        )
        
        # Display options
        parser.add_argument(
            '--no-display', 
            action='store_true',
            help='Run in headless mode (no GUI)'
        )
        parser.add_argument(
            '--fullscreen', 
            action='store_true',
            help='Start in fullscreen mode'
        )
        parser.add_argument(
            '--window-size', 
            type=str, 
            metavar='WIDTHxHEIGHT',
            help='Set window size (e.g., 1280x720)'
        )
        
        # Model parameters
        parser.add_argument(
            '--confidence', 
            type=float, 
            metavar='THRESHOLD',
            help='Detection confidence threshold (0.0-1.0)'
        )
        parser.add_argument(
            '--device', 
            choices=['auto', 'cpu', 'cuda', 'mps'],
            help='Device for inference (default: auto)'
        )
        
        # Output options
        parser.add_argument(
            '--save-frames', 
            action='store_true',
            help='Save processed frames to files'
        )
        parser.add_argument(
            '--output-dir', 
            type=str, 
            default='output',
            metavar='PATH',
            help='Output directory for saved frames'
        )
        
        # System info
        parser.add_argument(
            '--info', 
            action='store_true',
            help='Show system information and exit'
        )
        parser.add_argument(
            '--version', 
            action='version',
            version='%(prog)s 1.0.0'
        )
        
        return parser
    
    def show_system_info(self):
        """Display system information"""
        platform_info = get_platform_info()
        
        print("=" * 60)
        print("VISION TRACKER - SYSTEM INFORMATION")
        print("=" * 60)
        print(f"System: {platform_info.system} {platform_info.version}")
        print(f"Architecture: {platform_info.architecture}")
        print(f"Python: {platform_info.python_version}")
        print(f"WSL: {'Yes' if platform_info.is_wsl else 'No'}")
        print(f"Docker: {'Yes' if platform_info.is_docker else 'No'}")
        print(f"GUI Available: {'Yes' if platform_info.has_gui else 'No'}")
        
        # Check dependencies
        print("\nDependencies:")
        try:
            import cv2
            print(f"✓ OpenCV: {cv2.__version__}")
        except ImportError:
            print("✗ OpenCV: Not available")
        
        try:
            import torch
            print(f"✓ PyTorch: {torch.__version__}")
            print(f"  CUDA Available: {torch.cuda.is_available()}")
            if hasattr(torch.backends, 'mps'):
                print(f"  MPS Available: {torch.backends.mps.is_available()}")
        except ImportError:
            print("✗ PyTorch: Not available")
        
        try:
            from ultralytics import YOLO
            print("✓ Ultralytics YOLO: Available")
        except ImportError:
            print("✗ Ultralytics YOLO: Not available")
        
        print("=" * 60)
    
    def list_backend_models(self, backend_name: str):
        """List available models for a backend"""
        from ..models.factory import ModelFactory
        
        try:
            models = ModelFactory.list_models(backend_name)
            metadata = ModelFactory.get_backend_metadata(backend_name)
            
            print("=" * 60)
            print(f"AVAILABLE MODELS - {backend_name.upper()}")
            print("=" * 60)
            
            if metadata:
                print(f"Description: {metadata.description}")
                print(f"Capabilities: {', '.join(metadata.capabilities)}")
                print()
            
            if models:
                print("Available Models:")
                for model_key, model_path in models.items():
                    print(f"  {model_key:<15} -> {model_path}")
            else:
                print("No predefined models available for this backend")
            
            print("=" * 60)
            
        except Exception as e:
            print(f"Error listing models for {backend_name}: {e}")
            
            # Show available backends
            available = ModelFactory.get_available_backends()
            if available:
                print(f"Available backends: {', '.join(available)}")
            else:
                print("No backends available")
    
    def load_configuration(self, args) -> Config:
        """Load and configure system settings"""
        # Load base configuration
        if args.config:
            config = load_config(args.config)
        else:
            config = Config()
        
        # Override with command line arguments
        if args.confidence is not None:
            config.model.confidence_threshold = args.confidence
        
        if args.device:
            config.model.device = args.device
        
        if args.backend:
            config.model.backend = args.backend
        
        if args.model:
            config.model.name = args.model
        
        if args.window_size:
            try:
                width, height = map(int, args.window_size.split('x'))
                config.display.window_width = width
                config.display.window_height = height
            except ValueError:
                self.logger.error(f"Invalid window size format: {args.window_size}")
        
        if args.fullscreen:
            config.display.fullscreen = True
        
        if args.log_level:
            config.logging.level = args.log_level
        
        if args.log_file:
            config.logging.file = args.log_file
        
        return config
    
    def determine_source(self, args):
        """Determine input source from arguments"""
        if args.test:
            return None, True  # source, test_mode
        elif args.camera is not None:
            return args.camera, False
        elif args.video:
            video_path = Path(args.video)
            if not video_path.exists():
                raise FileNotFoundError(f"Video file not found: {video_path}")
            return str(video_path), False
        else:
            # Default: try camera 0, fallback to test mode
            return 0, False
    
    def run(self, args=None):
        """Main entry point"""
        parser = self.create_parser()
        args = parser.parse_args(args)
        
        # Show system info if requested
        if args.info:
            self.show_system_info()
            return 0
        
        # List models if requested
        if args.list_models:
            self.list_backend_models(args.list_models)
            return 0
        
        try:
            # Load configuration
            self.config = self.load_configuration(args)
            
            # Setup logging
            setup_logging(
                level=self.config.logging.level,
                log_file=self.config.logging.file,
                use_colors=True
            )
            
            self.logger.info("Starting Vision Tracker CLI")
            
            # Check if display is available
            platform_info = get_platform_info()
            if args.no_display or not platform_info.has_gui:
                self.logger.info("Running in headless mode")
            
            # Determine source
            source, test_mode = self.determine_source(args)
            
            # Initialize tracker
            force_headless = args.no_display or not platform_info.has_gui
            self.tracker = VisionTracker(self.config, force_headless=force_headless)
            
            # Setup callbacks if needed
            if args.save_frames:
                output_dir = Path(args.output_dir)
                output_dir.mkdir(exist_ok=True)
                self._setup_frame_saving_callback(output_dir)
            
            # Determine backends to preload
            preload_backends = None
            if args.preload_backends:
                preload_backends = args.preload_backends
                self.logger.info(f"Will preload backends: {preload_backends}")
            
            # Initialize and start
            if not self.tracker.initialize(
                source=source, 
                test_mode=test_mode, 
                preload_backends=preload_backends
            ):
                self.logger.error("Failed to initialize tracker")
                return 1
            
            self.logger.info("Tracker initialized successfully")
            self._print_usage_info()
            
            # Start tracking
            self.tracker.start()
            
            return 0
            
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
            return 0
        except Exception as e:
            self.logger.error(f"Application error: {e}")
            return 1
        finally:
            if self.tracker:
                self.tracker.stop()
    
    def _setup_frame_saving_callback(self, output_dir: Path):
        """Setup frame saving callback"""
        frame_count = 0
        
        def save_frame(frame, detections):
            nonlocal frame_count
            if frame_count % 30 == 0:  # Save every 30th frame
                filename = output_dir / f"frame_{frame_count:06d}.jpg"
                import cv2
                cv2.imwrite(str(filename), frame)
                self.logger.info(f"Saved frame: {filename}")
            frame_count += 1
        
        self.tracker.set_frame_callback(save_frame)
    
    def _print_usage_info(self):
        """Print usage information"""
        print("\n" + "=" * 60)
        print("VISION TRACKER - CONTROLS")
        print("=" * 60)
        print("Keyboard Controls:")
        print("  'q' or ESC  - Quit application")
        print("  SPACE       - Pause/Resume")
        print("  's'         - Save screenshot")
        print("  'f'         - Toggle fullscreen")
        print("  'r'         - Reset window size")
        
        # Show backend switching controls if enabled
        if self.tracker and self.tracker.is_backend_switching_enabled():
            available_backends = self.tracker.get_available_backends()
            print("\nBackend Switching:")
            print("  'n'         - Next backend")
            print("  'b'         - Previous backend")
            for i, backend in enumerate(available_backends[:3]):  # Show first 3
                print(f"  '{i+1}'         - Switch to {backend.upper()}")
            print("  'i'         - Show backend info")
            print(f"\nLoaded backends: {', '.join(b.upper() for b in available_backends)}")
        
        print("\nPress Ctrl+C to stop")
        print("=" * 60)


def main():
    """Main entry point for CLI"""
    cli = VisionTrackerCLI()
    return cli.run()


if __name__ == '__main__':
    sys.exit(main())