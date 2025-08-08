FROM python:3.9-slim

# Set environment variables to prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    libgtk-3-0 \
    libgl1-mesa-glx \
    libglu1-mesa \
    libx11-xcb1 \
    libxcb1 \
    libxv1 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    v4l-utils \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY vision_tracker.py .
COPY generate_sample_video.py .
COPY docker_entrypoint.sh .
RUN chmod +x docker_entrypoint.sh

ENV DISPLAY=:0
ENV QT_X11_NO_MITSHM=1
ENV OPENCV_VIDEOIO_PRIORITY_V4L2=1

# Generate a sample video for testing if needed
RUN python generate_sample_video.py --duration 10 --output /app/sample_video.mp4 || true

# Use entrypoint script for intelligent mode selection
ENTRYPOINT ["/app/docker_entrypoint.sh"]