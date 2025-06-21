import json
import boto3
import base64
import os
from typing import Dict, Any
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
bedrock_client = boto3.client('bedrock-runtime', region_name=os.environ.get('BEDROCK_REGION', 'us-east-1'))
s3_client = boto3.client('s3')

def process_sign(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Process sign language video frames using Amazon Bedrock
    """
    try:
        # Parse the incoming event
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
        
        # Extract video frame data
        frame_data = body.get('frame_data')
        timestamp = body.get('timestamp')
        device_id = body.get('device_id', 'default')
        
        if not frame_data:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No frame data provided'})
            }
        
        # Process the frame with Bedrock
        translation_result = process_frame_with_bedrock(frame_data)
        
        # Store result in S3 for historical analysis
        store_result_in_s3(device_id, timestamp, translation_result)
        
        # Return the translation
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            },
            'body': json.dumps({
                'translation': translation_result.get('text', ''),
                'confidence': translation_result.get('confidence', 0.0),
                'timestamp': timestamp,
                'device_id': device_id
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing sign language frame: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Processing error: {str(e)}'})
        }

def process_frame_with_bedrock(frame_data: str) -> Dict[str, Any]:
    """
    Use Amazon Bedrock to analyze video frame for sign language
    """
    try:
        # For now, we'll use Claude with vision capabilities
        # In production, you'd use a specialized computer vision model
        
        prompt = """
        You are a sign language interpreter. Analyze this video frame and identify any American Sign Language (ASL) gestures or signs being performed. 
        
        Provide:
        1. The interpreted text/words if recognizable signs are present
        2. A confidence score (0.0-1.0)
        3. Description of hand positions and movements observed
        
        If no clear signs are detected, respond with "No clear signs detected" and confidence 0.0.
        
        Respond in JSON format:
        {
            "text": "interpreted words or 'No clear signs detected'",
            "confidence": 0.0-1.0,
            "description": "description of observed gestures"
        }
        """
        
        # Prepare the request for Bedrock
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 200,
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
                                "data": frame_data
                            }
                        }
                    ]
                }
            ]
        }
        
        # Call Bedrock with Claude 3.5 Sonnet v2 (latest version)
        response = bedrock_client.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            body=json.dumps(request_body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        content = response_body['content'][0]['text']
        
        # Try to parse as JSON, fallback to text extraction
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            # Fallback parsing
            result = {
                "text": content[:100],  # First 100 chars
                "confidence": 0.5,
                "description": "Raw response from model"
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Error calling Bedrock: {str(e)}")
        return {
            "text": "Error processing frame",
            "confidence": 0.0,
            "description": f"Processing error: {str(e)}"
        }

def store_result_in_s3(device_id: str, timestamp: str, result: Dict[str, Any]) -> None:
    """
    Store processing result in S3 for historical analysis
    """
    try:
        bucket_name = os.environ.get('DATA_BUCKET')
        if not bucket_name:
            logger.warning("No S3 bucket configured, skipping storage")
            return
        
        key = f"results/{device_id}/{timestamp}.json"
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=json.dumps(result),
            ContentType='application/json'
        )
        
        logger.info(f"Stored result in S3: {bucket_name}/{key}")
        
    except Exception as e:
        logger.error(f"Error storing result in S3: {str(e)}")

def websocket_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle WebSocket connections for real-time communication
    """
    try:
        route_key = event.get('requestContext', {}).get('routeKey')
        
        if route_key == '$connect':
            return {'statusCode': 200}
        elif route_key == '$disconnect':
            return {'statusCode': 200}
        elif route_key == 'process_frame':
            # Process frame data received via WebSocket
            body = json.loads(event.get('body', '{}'))
            result = process_frame_with_bedrock(body.get('frame_data', ''))
            
            # Send result back via WebSocket
            # Implementation would require API Gateway Management API
            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }
        
        return {'statusCode': 400, 'body': 'Unknown route'}
        
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}