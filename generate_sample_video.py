#!/usr/bin/env python3
import cv2
import numpy as np
import time
from pathlib import Path

def generate_sample_video(output_path="sample_video.mp4", duration=30, fps=30):
    """Generate a sample video with moving objects for testing"""
    
    # Video settings
    width, height = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    total_frames = duration * fps
    print(f"Generating {duration} second video at {fps} FPS ({total_frames} frames)...")
    
    for frame_num in range(total_frames):
        # Create base frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add gradient background
        for i in range(height):
            frame[i, :] = [30 + i//4, 20 + i//6, 40 + i//8]
        
        # Time-based animation
        t = frame_num / fps
        
        # Moving person simulation (circular motion)
        person_x = int(width/2 + 150 * np.sin(t * 0.5))
        person_y = int(height/2 + 80 * np.cos(t * 0.5))
        # Body
        cv2.ellipse(frame, (person_x, person_y), (30, 50), 0, 0, 360, (100, 150, 200), -1)
        # Head
        cv2.circle(frame, (person_x, person_y - 60), 20, (200, 150, 100), -1)
        
        # Moving car simulation (left to right)
        car_x = int((t * 50) % (width + 100) - 50)
        car_y = height - 100
        cv2.rectangle(frame, (car_x, car_y), (car_x + 80, car_y + 40), (50, 50, 200), -1)
        # Windows
        cv2.rectangle(frame, (car_x + 10, car_y + 5), (car_x + 35, car_y + 20), (150, 150, 255), -1)
        cv2.rectangle(frame, (car_x + 45, car_y + 5), (car_x + 70, car_y + 20), (150, 150, 255), -1)
        
        # Moving bicycle simulation
        bike_x = int(width - (t * 40) % (width + 100))
        bike_y = height - 150
        # Wheels
        cv2.circle(frame, (bike_x, bike_y), 15, (100, 100, 100), 2)
        cv2.circle(frame, (bike_x + 40, bike_y), 15, (100, 100, 100), 2)
        # Frame
        cv2.line(frame, (bike_x, bike_y), (bike_x + 40, bike_y), (150, 150, 150), 2)
        cv2.line(frame, (bike_x, bike_y), (bike_x + 20, bike_y - 30), (150, 150, 150), 2)
        cv2.line(frame, (bike_x + 40, bike_y), (bike_x + 20, bike_y - 30), (150, 150, 150), 2)
        
        # Static objects
        # Chair
        cv2.rectangle(frame, (500, 300), (560, 380), (139, 69, 19), -1)
        cv2.rectangle(frame, (500, 250), (560, 300), (169, 99, 49), -1)
        
        # Potted plant
        cv2.ellipse(frame, (100, 350), (30, 20), 0, 0, 360, (50, 100, 50), -1)
        cv2.rectangle(frame, (85, 360), (115, 400), (100, 50, 0), -1)
        
        # Dog (moving)
        dog_x = int(200 + 100 * np.sin(t * 2))
        dog_y = int(350 + 20 * np.sin(t * 4))
        # Body
        cv2.ellipse(frame, (dog_x, dog_y), (25, 15), 0, 0, 360, (100, 80, 60), -1)
        # Head
        cv2.circle(frame, (dog_x - 20, dog_y - 5), 10, (120, 100, 80), -1)
        # Tail
        cv2.ellipse(frame, (dog_x + 25, dog_y - 10), (10, 5), 45, 0, 360, (80, 60, 40), -1)
        
        # Add some noise for realism
        noise = np.random.normal(0, 3, frame.shape).astype(np.uint8)
        frame = cv2.add(frame, noise)
        
        # Add timestamp
        timestamp = f"Frame: {frame_num:04d} | Time: {t:.1f}s"
        cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Write frame
        out.write(frame)
        
        # Progress indicator
        if frame_num % fps == 0:
            print(f"  Generated {frame_num}/{total_frames} frames ({int(frame_num/total_frames*100)}%)")
    
    out.release()
    print(f"Sample video saved: {output_path}")
    print(f"File size: {Path(output_path).stat().st_size / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate sample video for vision tracking tests')
    parser.add_argument('--output', type=str, default='sample_video.mp4', help='Output video file path')
    parser.add_argument('--duration', type=int, default=30, help='Video duration in seconds')
    parser.add_argument('--fps', type=int, default=30, help='Frames per second')
    
    args = parser.parse_args()
    
    generate_sample_video(args.output, args.duration, args.fps)