#!/usr/bin/env python3
"""
Vision Tracker - Main Entry Point

Professional real-time object detection and tracking system.
"""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from vision_tracker.cli.main import main

if __name__ == '__main__':
    sys.exit(main())