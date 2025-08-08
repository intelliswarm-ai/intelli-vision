"""
Core Data Types

Defines data structures used throughout the vision tracker system.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class Detection:
    """
    Object detection result
    """
    class_id: int
    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    center: Tuple[int, int]
    area: float