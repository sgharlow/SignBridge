#!/usr/bin/env python3
"""
Test script for Bedrock integration with sign language processing
"""

import json
import boto3
import base64
import sys
import os
from PIL import Image, ImageDraw, ImageFont
import io

def create_test_image():
    """Create a test image with sign language gesture simulation"""
    # Create a simple test image
    img = Image.new('RGB', (640, 480), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple hand gesture representation
    # Draw palm
    draw.ellipse([250, 200, 350, 300], fill='peachpuff', outline='black', width=2)
    
    # Draw fingers
    for i, finger_pos in enumerate([(270, 150), (290, 140), (310, 130), (330, 140)]):
        draw.ellipse([finger_pos[0]-10, finger_pos[1]-30, finger_pos[0]+10, finger_pos[1]+30], 
                     fill='peachpuff', outline='black', width=2)
    
    # Draw thumb
    draw.ellipse([220, 220, 240, 260], fill='peachpuff', outline='black', width=2)
    
    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    draw.text((200, 350), "ASL Sign: HELLO", fill='black', font=font)
    draw.text((200, 380), "Test Image for SignToMe", fill='gray', font=font)
    
    return img

def image_to_base64(image):
    """Convert PIL Image to base64 string"""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=85)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def test_bedrock_sign_detection():
    """Test the sign language detection with Bedrock"""
    print("Testing Bedrock sign language detection...")
    
    # Initialize Bedrock client
    bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    # Create test image
    test_image = create_test_image()
    test_image.save('/tmp/test_sign.jpg')  # Save for reference
    print("Test image created and saved to /tmp/test_sign.jpg")
    
    # Convert to base64
    image_base64 = image_to_base64(test_image)
    
    # Prepare the request
    prompt = """
    You are an expert sign language interpreter specializing in American Sign Language (ASL). 
    Analyze this image and determine if it contains any recognizable ASL signs or gestures.
    
    Please provide your analysis in the following JSON format:
    {
        "sign_detected": true/false,
        "sign_name": "name of the sign if detected, or null",
        "confidence": 0.0-1.0,
        "description": "detailed description of what you observe",
        "hand_position": "description of hand position and orientation",
        "recommendations": "any suggestions for improving sign clarity"
    }
    
    Be very specific about hand positions, finger orientations, and movement patterns you can observe.
    """
    
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 300,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_base64
                        }
                    }
                ]
            }
        ]
    }
    
    try:
        # Call Bedrock
        print("Calling Bedrock API...")
        response = bedrock_client.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            body=json.dumps(request_body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        content = response_body['content'][0]['text']
        
        print("\n" + "="*50)
        print("BEDROCK RESPONSE:")
        print("="*50)
        print(content)
        print("="*50)
        
        # Try to parse as JSON
        try:
            result = json.loads(content)
            print("\nParsed JSON Result:")
            for key, value in result.items():
                print(f"  {key}: {value}")
        except json.JSONDecodeError:
            print("\nNote: Response is not valid JSON, using raw text")
        
        return True
        
    except Exception as e:
        print(f"Error calling Bedrock: {str(e)}")
        return False

def test_lambda_handler():
    """Test the Lambda handler function locally"""
    print("\nTesting Lambda handler function...")
    
    # Import the handler
    sys.path.append('/mnt/c/Users/sghar/CascadeProjects/signtome/backend/lambda')
    from handler import process_sign
    
    # Create test image
    test_image = create_test_image()
    image_base64 = image_to_base64(test_image)
    
    # Create test event
    test_event = {
        'body': json.dumps({
            'frame_data': image_base64,
            'timestamp': '2025-06-21T02:00:00Z',
            'device_id': 'test-device-001'
        })
    }
    
    # Test the handler
    try:
        result = process_sign(test_event, None)
        print("\nLambda Handler Result:")
        print(f"Status Code: {result['statusCode']}")
        print(f"Response Body: {result['body']}")
        
        if result['statusCode'] == 200:
            response_data = json.loads(result['body'])
            print("\nProcessed Data:")
            for key, value in response_data.items():
                print(f"  {key}: {value}")
        
        return result['statusCode'] == 200
        
    except Exception as e:
        print(f"Error testing Lambda handler: {str(e)}")
        return False

def main():
    """Main test function"""
    print("SignToMe Bedrock Integration Test")
    print("=" * 40)
    
    # Test 1: Direct Bedrock API call
    bedrock_success = test_bedrock_sign_detection()
    
    # Test 2: Lambda handler function
    if bedrock_success:
        lambda_success = test_lambda_handler()
    else:
        print("Skipping Lambda test due to Bedrock failure")
        lambda_success = False
    
    # Summary
    print("\n" + "="*40)
    print("TEST SUMMARY:")
    print("="*40)
    print(f"Bedrock API Test: {'PASS' if bedrock_success else 'FAIL'}")
    print(f"Lambda Handler Test: {'PASS' if lambda_success else 'FAIL'}")
    
    if bedrock_success and lambda_success:
        print("\n✅ All tests passed! Ready for deployment.")
        return 0
    else:
        print("\n❌ Some tests failed. Check configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())