#!/usr/bin/env python3
"""
Test the deployed SignToMe API with a proper test image
"""

import requests
import json
import base64
import io
from PIL import Image, ImageDraw, ImageFont

def create_hello_sign_image():
    """Create a realistic test image showing ASL 'HELLO' sign"""
    # Create a 640x480 image with a realistic background
    img = Image.new('RGB', (640, 480), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple representation of the ASL "HELLO" sign
    # In ASL, "HELLO" is signed by placing fingers together and moving them away from forehead
    
    # Draw face outline
    draw.ellipse([220, 150, 420, 350], fill='peachpuff', outline='darkgray', width=2)
    
    # Draw hand near forehead (simplified representation)
    # Palm facing out, fingers extended
    hand_x, hand_y = 180, 120
    
    # Draw palm
    draw.ellipse([hand_x, hand_y, hand_x+60, hand_y+80], fill='peachpuff', outline='black', width=2)
    
    # Draw individual fingers
    finger_positions = [
        (hand_x+10, hand_y-30, hand_x+20, hand_y+10),  # Index finger
        (hand_x+25, hand_y-35, hand_x+35, hand_y+5),   # Middle finger  
        (hand_x+40, hand_y-30, hand_x+50, hand_y+10),  # Ring finger
        (hand_x+55, hand_y-25, hand_x+65, hand_y+15),  # Pinky
    ]
    
    for finger in finger_positions:
        draw.ellipse(finger, fill='peachpuff', outline='black', width=1)
    
    # Draw thumb
    draw.ellipse([hand_x-15, hand_y+20, hand_x+5, hand_y+50], fill='peachpuff', outline='black', width=1)
    
    # Add motion lines to indicate movement away from forehead
    for i in range(3):
        start_x = hand_x + 70 + (i * 10)
        draw.line([start_x, hand_y+20, start_x+15, hand_y+25], fill='gray', width=2)
    
    # Add descriptive text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font = ImageFont.load_default()
        small_font = font
    
    # Title
    draw.text((200, 30), "ASL Sign: HELLO", fill='black', font=font)
    
    # Description
    draw.text((50, 400), "Hand starts at forehead, fingers move outward", fill='darkblue', font=small_font)
    draw.text((50, 420), "SignToMe Test Image - June 2025", fill='gray', font=small_font)
    
    # Add some context elements
    draw.rectangle([10, 10, 630, 470], outline='darkgray', width=3)
    
    return img

def test_api_endpoint():
    """Test the SignToMe API with the test image"""
    
    # API endpoint
    api_url = "https://6ddpddg0g3.execute-api.us-east-1.amazonaws.com/prod/process"
    
    print("Creating test image for ASL 'HELLO' sign...")
    test_image = create_hello_sign_image()
    
    # Convert to base64
    buffered = io.BytesIO()
    test_image.save(buffered, format="JPEG", quality=90)
    image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    print(f"Image size: {len(image_base64)} characters")
    
    # Prepare request
    payload = {
        "frame_data": image_base64,
        "timestamp": "2025-06-21T09:00:00Z",
        "device_id": "test-device-hello"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Sending request to: {api_url}")
    print(f"Payload size: {len(json.dumps(payload))} bytes")
    
    try:
        # Make the API call
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n🎉 SUCCESS! API Response:")
            print("="*50)
            print(f"Translation: {result.get('translation', 'N/A')}")
            print(f"Confidence: {result.get('confidence', 'N/A')}")
            print(f"Timestamp: {result.get('timestamp', 'N/A')}")
            print(f"Device ID: {result.get('device_id', 'N/A')}")
            print("="*50)
            
            # Save test image for reference
            test_image.save('/tmp/test_hello_sign.jpg', quality=90)
            print(f"\nTest image saved to: /tmp/test_hello_sign.jpg")
            
        else:
            print(f"\n❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_api_endpoint()