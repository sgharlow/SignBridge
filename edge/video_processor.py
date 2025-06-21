#!/usr/bin/env python3
"""
SignToMe Edge Video Processor
Captures video frames and sends to AWS IoT Core for processing
"""

import cv2
import base64
import json
import time
import threading
from datetime import datetime
import logging
import os
import sys

# AWS IoT SDK
try:
    from awsiot import mqtt_connection_builder
    from awscrt import io, mqtt, auth, http
    from awsiot.greengrass_discovery import DiscoveryClient
except ImportError:
    print("AWS IoT SDK not available. Running in simulation mode.")
    mqtt_available = False
else:
    mqtt_available = True

# Configuration
CAMERA_DEVICE = int(os.environ.get('CAMERA_DEVICE', '0'))
FRAME_RATE = int(os.environ.get('FRAME_RATE', '10'))
PROCESSING_INTERVAL = float(os.environ.get('PROCESSING_INTERVAL', '0.5'))
MQTT_TOPIC = os.environ.get('MQTT_TOPIC', 'signtome/frames')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
DEVICE_ID = os.environ.get('DEVICE_ID', 'edge-device-001')

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        self.camera = None
        self.mqtt_connection = None
        self.running = False
        self.last_process_time = 0
        
    def initialize_camera(self):
        """Initialize camera connection"""
        try:
            self.camera = cv2.VideoCapture(CAMERA_DEVICE)
            if not self.camera.isOpened():
                # Fallback to simulation mode
                logger.warning("Camera not available, using simulation mode")
                self.camera = None
                return False
                
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, FRAME_RATE)
            
            logger.info("Camera initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}")
            return False
    
    def initialize_mqtt(self):
        """Initialize MQTT connection to AWS IoT Core"""
        if not mqtt_available:
            logger.warning("MQTT not available, using simulation mode")
            return False
            
        try:
            # In production, use certificates from Greengrass
            # For simulation, we'll skip actual MQTT connection
            logger.info("MQTT would be initialized here in production")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize MQTT: {e}")
            return False
    
    def capture_frame(self):
        """Capture a frame from camera or generate simulation frame"""
        if self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                return frame
        
        # Simulation mode - create a dummy frame
        import numpy as np
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Add some text to indicate simulation
        cv2.putText(frame, f"SIMULATION MODE - {datetime.now().strftime('%H:%M:%S')}",
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "Sign language gestures would be captured here",
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
    
    def encode_frame(self, frame):
        """Encode frame as base64 JPEG"""
        try:
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            return frame_base64
        except Exception as e:
            logger.error(f"Failed to encode frame: {e}")
            return None
    
    def send_frame_to_cloud(self, frame_data):
        """Send frame data to AWS IoT Core"""
        try:
            message = {
                'device_id': DEVICE_ID,
                'timestamp': datetime.now().isoformat(),
                'frame_data': frame_data,
                'metadata': {
                    'resolution': '640x480',
                    'format': 'jpeg',
                    'region': AWS_REGION
                }
            }
            
            if self.mqtt_connection:
                # In production, publish to MQTT topic
                self.mqtt_connection.publish(
                    topic=MQTT_TOPIC,
                    payload=json.dumps(message),
                    qos=mqtt.QoS.AT_LEAST_ONCE
                )
                logger.info(f"Frame sent to topic: {MQTT_TOPIC}")
            else:
                # Simulation mode - log message
                logger.info(f"[SIMULATION] Would send frame to {MQTT_TOPIC}")
                logger.info(f"[SIMULATION] Frame size: {len(frame_data)} bytes")
                
        except Exception as e:
            logger.error(f"Failed to send frame: {e}")
    
    def process_video_stream(self):
        """Main video processing loop"""
        logger.info("Starting video processing...")
        
        while self.running:
            try:
                current_time = time.time()
                
                # Check if it's time to process a frame
                if current_time - self.last_process_time >= PROCESSING_INTERVAL:
                    # Capture frame
                    frame = self.capture_frame()
                    if frame is not None:
                        # Encode frame
                        frame_data = self.encode_frame(frame)
                        if frame_data:
                            # Send to cloud
                            self.send_frame_to_cloud(frame_data)
                    
                    self.last_process_time = current_time
                
                # Small delay to prevent CPU overload
                time.sleep(0.01)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                break
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                time.sleep(1)  # Brief pause on error
    
    def start(self):
        """Start the video processor"""
        self.running = True
        
        # Initialize components
        camera_ok = self.initialize_camera()
        mqtt_ok = self.initialize_mqtt()
        
        if not camera_ok and not mqtt_ok:
            logger.warning("Running in full simulation mode")
        
        # Start processing in separate thread
        processing_thread = threading.Thread(target=self.process_video_stream)
        processing_thread.daemon = True
        processing_thread.start()
        
        logger.info("Video processor started. Press Ctrl+C to stop.")
        
        try:
            # Keep main thread alive
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.stop()
    
    def stop(self):
        """Stop the video processor"""
        self.running = False
        
        if self.camera:
            self.camera.release()
        
        if self.mqtt_connection:
            self.mqtt_connection.disconnect()
        
        logger.info("Video processor stopped")

def main():
    """Main entry point"""
    processor = VideoProcessor()
    
    try:
        processor.start()
    except Exception as e:
        logger.error(f"Failed to start processor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()