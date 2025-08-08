"""
Platform Detection and System Utilities

Handles platform-specific detection and configuration for optimal performance
across different operating systems and environments.
"""

import os
import platform
import subprocess
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class PlatformInfo:
    """Platform information container"""
    system: str
    version: str
    architecture: str
    is_windows: bool
    is_linux: bool
    is_macos: bool
    is_wsl: bool
    is_docker: bool
    python_version: str
    has_gui: bool


class PlatformDetector:
    """Platform detection and system information utilities"""
    
    @staticmethod
    def detect() -> PlatformInfo:
        """
        Detect current platform and environment
        
        Returns:
            PlatformInfo object with detected information
        """
        system = platform.system()
        version = platform.version()
        architecture = platform.machine()
        python_version = platform.python_version()
        
        is_windows = system == 'Windows'
        is_linux = system == 'Linux'
        is_macos = system == 'Darwin'
        
        # WSL detection
        is_wsl = False
        if is_linux:
            try:
                with open('/proc/version', 'r') as f:
                    version_info = f.read().lower()
                    is_wsl = 'microsoft' in version_info or 'wsl' in version_info
            except (FileNotFoundError, PermissionError):
                pass
        
        # Docker detection
        is_docker = os.path.exists('/.dockerenv') or os.path.exists('/proc/1/cgroup')
        if not is_docker and os.path.exists('/proc/1/cgroup'):
            try:
                with open('/proc/1/cgroup', 'r') as f:
                    is_docker = 'docker' in f.read()
            except (FileNotFoundError, PermissionError):
                pass
        
        # GUI availability detection
        has_gui = PlatformDetector._detect_gui_availability(system, is_wsl, is_docker)
        
        platform_info = PlatformInfo(
            system=system,
            version=version,
            architecture=architecture,
            is_windows=is_windows,
            is_linux=is_linux,
            is_macos=is_macos,
            is_wsl=is_wsl,
            is_docker=is_docker,
            python_version=python_version,
            has_gui=has_gui
        )
        
        logger.debug(f"Platform detected: {platform_info}")
        return platform_info
    
    @staticmethod
    def _detect_gui_availability(system: str, is_wsl: bool, is_docker: bool) -> bool:
        """Detect if GUI is available"""
        if is_docker:
            return bool(os.environ.get('DISPLAY'))
        
        if system == 'Windows':
            return True
        
        if system == 'Darwin':  # macOS
            return True
        
        if system == 'Linux':
            # Check for X11 display
            if os.environ.get('DISPLAY'):
                try:
                    result = subprocess.run(['xdpyinfo'], 
                                          capture_output=True, 
                                          timeout=2)
                    return result.returncode == 0
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
            
            # Check for Wayland
            if os.environ.get('WAYLAND_DISPLAY'):
                return True
            
            # WSL with WSLg
            if is_wsl and os.environ.get('DISPLAY'):
                return True
        
        return False
    
    @staticmethod
    def get_camera_backends() -> List[Tuple[str, int]]:
        """
        Get available camera backends for the current platform
        
        Returns:
            List of (backend_name, opencv_backend_id) tuples
        """
        import cv2
        
        platform_info = PlatformDetector.detect()
        backends = []
        
        if platform_info.is_windows:
            backends = [
                ('DirectShow', cv2.CAP_DSHOW),
                ('Media Foundation', cv2.CAP_MSMF),
                ('Default', cv2.CAP_ANY)
            ]
        elif platform_info.is_linux:
            backends = [
                ('V4L2', cv2.CAP_V4L2),
                ('GStreamer', cv2.CAP_GSTREAMER),
                ('Default', cv2.CAP_ANY)
            ]
        elif platform_info.is_macos:
            backends = [
                ('AVFoundation', cv2.CAP_AVFOUNDATION),
                ('Default', cv2.CAP_ANY)
            ]
        else:
            backends = [('Default', cv2.CAP_ANY)]
        
        logger.debug(f"Available camera backends: {[name for name, _ in backends]}")
        return backends
    
    @staticmethod
    def get_optimal_thread_count() -> int:
        """Get optimal thread count for the current system"""
        try:
            import multiprocessing
            cpu_count = multiprocessing.cpu_count()
            
            # Use all cores but cap at 8 to avoid diminishing returns
            optimal_count = min(cpu_count, 8)
            logger.debug(f"Optimal thread count: {optimal_count} (CPU cores: {cpu_count})")
            return optimal_count
        except Exception:
            logger.warning("Could not determine CPU count, using default of 2")
            return 2
    
    @staticmethod
    def check_gpu_availability() -> Dict[str, bool]:
        """Check GPU acceleration availability"""
        gpu_info = {
            'cuda': False,
            'opencl': False,
            'mps': False  # Apple Metal Performance Shaders
        }
        
        try:
            import torch
            gpu_info['cuda'] = torch.cuda.is_available()
            if hasattr(torch.backends, 'mps'):
                gpu_info['mps'] = torch.backends.mps.is_available()
        except ImportError:
            logger.debug("PyTorch not available for GPU detection")
        
        try:
            import cv2
            gpu_info['opencl'] = cv2.ocl.haveOpenCL()
        except (ImportError, AttributeError):
            logger.debug("OpenCV OpenCL detection not available")
        
        logger.debug(f"GPU availability: {gpu_info}")
        return gpu_info
    
    @staticmethod
    def get_memory_info() -> Dict[str, int]:
        """Get system memory information in bytes"""
        memory_info = {}
        
        try:
            import psutil
            memory = psutil.virtual_memory()
            memory_info = {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percentage': memory.percent
            }
        except ImportError:
            try:
                # Fallback for systems without psutil
                if platform.system() == 'Linux':
                    with open('/proc/meminfo', 'r') as f:
                        lines = f.readlines()
                        for line in lines:
                            if line.startswith('MemTotal:'):
                                memory_info['total'] = int(line.split()[1]) * 1024
                            elif line.startswith('MemAvailable:'):
                                memory_info['available'] = int(line.split()[1]) * 1024
            except Exception as e:
                logger.warning(f"Could not get memory info: {e}")
        
        logger.debug(f"Memory info: {memory_info}")
        return memory_info


# Global platform info instance
_platform_info: Optional[PlatformInfo] = None


def get_platform_info() -> PlatformInfo:
    """Get cached platform information"""
    global _platform_info
    if _platform_info is None:
        _platform_info = PlatformDetector.detect()
    return _platform_info