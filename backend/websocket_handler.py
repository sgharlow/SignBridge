#!/usr/bin/env python3
"""
WebSocket handler for real-time sign language processing
"""

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
apigateway_client = boto3.client('apigatewaymanagementapi')

class WebSocketProcessor:
    """Handles WebSocket connections and real-time processing"""
    
    def __init__(self, endpoint_url: str):
        self.endpoint_url = endpoint_url
        self.apigateway_client = boto3.client(
            'apigatewaymanagementapi',
            endpoint_url=endpoint_url
        )
    
    async def send_message(self, connection_id: str, message: Dict[str, Any]) -> bool:
        """Send message to WebSocket client"""
        try:
            self.apigateway_client.post_to_connection(
                ConnectionId=connection_id,
                Data=json.dumps(message)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {connection_id}: {e}")
            return False
    
    def process_frame_realtime(self, frame_data: str, connection_id: str) -> Dict[str, Any]:
        """Process frame and send real-time updates"""
        
        # Send processing started message
        self.send_message(connection_id, {
            'type': 'processing_started',
            'timestamp': json.dumps(None, default=str)
        })
        
        try:
            # Quick frame validation
            if not frame_data or len(frame_data) < 100:
                result = {
                    'type': 'translation_result',
                    'translation': 'Invalid frame data',
                    'confidence': 0.0,
                    'error': 'Frame too small or empty'
                }
                self.send_message(connection_id, result)
                return result
            
            # Process with Bedrock (simplified for demo)
            prompt = """
            You are a sign language interpreter. Analyze this image for American Sign Language (ASL) signs.
            
            Respond in this exact JSON format:
            {
                "translation": "the interpreted text or 'No signs detected'",
                "confidence": 0.0-1.0,
                "description": "brief description of what you see"
            }
            
            Keep responses concise and focus on common ASL signs.
            """
            
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 150,
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
            
            # Call Bedrock
            response = bedrock_client.invoke_model(
                modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            content = response_body['content'][0]['text']
            
            # Parse JSON response
            try:
                bedrock_result = json.loads(content)
            except json.JSONDecodeError:
                bedrock_result = {
                    "translation": content[:50] + "..." if len(content) > 50 else content,
                    "confidence": 0.3,
                    "description": "Raw model response"
                }
            
            # Send final result
            result = {
                'type': 'translation_result',
                'translation': bedrock_result.get('translation', 'Processing error'),
                'confidence': bedrock_result.get('confidence', 0.0),
                'description': bedrock_result.get('description', ''),
                'timestamp': json.dumps(None, default=str)
            }
            
            self.send_message(connection_id, result)
            return result
            
        except Exception as e:
            error_result = {
                'type': 'translation_result',
                'translation': 'Processing failed',
                'confidence': 0.0,
                'error': str(e),
                'timestamp': json.dumps(None, default=str)
            }
            self.send_message(connection_id, error_result)
            return error_result

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main WebSocket Lambda handler"""
    
    route_key = event.get('requestContext', {}).get('routeKey')
    connection_id = event.get('requestContext', {}).get('connectionId')
    
    # Get API Gateway endpoint URL
    domain_name = event.get('requestContext', {}).get('domainName')
    stage = event.get('requestContext', {}).get('stage')
    endpoint_url = f"https://{domain_name}/{stage}"
    
    processor = WebSocketProcessor(endpoint_url)
    
    try:
        if route_key == '$connect':
            logger.info(f"Client connected: {connection_id}")
            return {'statusCode': 200}
            
        elif route_key == '$disconnect':
            logger.info(f"Client disconnected: {connection_id}")
            return {'statusCode': 200}
            
        elif route_key == 'process_frame':
            # Parse message body
            body = json.loads(event.get('body', '{}'))
            frame_data = body.get('frame_data')
            
            if not frame_data:
                processor.send_message(connection_id, {
                    'type': 'error',
                    'message': 'No frame data provided'
                })
                return {'statusCode': 400}
            
            # Process frame in real-time
            result = processor.process_frame_realtime(frame_data, connection_id)
            
            return {'statusCode': 200}
            
        else:
            logger.warning(f"Unknown route: {route_key}")
            return {'statusCode': 400}
            
    except Exception as e:
        logger.error(f"WebSocket handler error: {e}")
        try:
            processor.send_message(connection_id, {
                'type': 'error',
                'message': f'Server error: {str(e)}'
            })
        except:
            pass
        return {'statusCode': 500}