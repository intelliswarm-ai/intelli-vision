"""
Vision Tracker Setup Script
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = requirements_path.read_text().strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="vision-tracker",
    version="1.0.0",
    description="Professional real-time object detection and tracking system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="IntelliSwarm AI",
    author_email="contact@intelliswarm.ai",
    url="https://github.com/intelliswarm-ai/vision-tracker",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
            "pre-commit"
        ],
        "gpu": [
            "torch>=1.12.0",
            "torchvision>=0.13.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "vision-tracker=vision_tracker.cli.main:main",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Multimedia :: Video :: Capture",
    ],
    keywords="computer-vision object-detection yolo tracking opencv pytorch",
    project_urls={
        "Bug Reports": "https://github.com/intelliswarm-ai/vision-tracker/issues",
        "Source": "https://github.com/intelliswarm-ai/vision-tracker",
        "Documentation": "https://vision-tracker.readthedocs.io/",
    },
)