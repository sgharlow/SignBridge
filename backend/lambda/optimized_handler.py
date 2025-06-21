import json
import boto3
import base64
import os
import time
from typing import Dict, Any
import logging

# Import our optimization modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from processing_optimizer import pipeline

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
bedrock_client = boto3.client('bedrock-runtime', region_name=os.environ.get('BEDROCK_REGION', 'us-east-1'))
s3_client = boto3.client('s3')

def process_sign_optimized(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Optimized sign language processing with caching and rate limiting
    """
    start_time = time.time()
    
    try:
        # Parse the incoming event
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
        
        # Extract request data
        frame_data = body.get('frame_data')
        timestamp = body.get('timestamp')
        device_id = body.get('device_id', 'default')
        
        if not frame_data:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'No frame data provided'})
            }
        
        # Use optimized processing pipeline
        result = pipeline.process_with_cache(frame_data, device_id)
        
        # If not a cached result, process with Bedrock
        if not result.get('cache_hit', False) and result.get('translation') == 'Sample sign detected':
            bedrock_result = process_with_bedrock(frame_data)
            result.update(bedrock_result)
        
        # Store result in S3 for analytics
        store_result_in_s3(device_id, timestamp, result)
        
        # Add performance metrics
        result.update({
            'timestamp': timestamp,
            'device_id': device_id,
            'total_latency': time.time() - start_time,
            'performance_stats': pipeline.get_performance_stats()
        })
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'translation': result.get('translation', 'Processing error'),
                'confidence': result.get('confidence', 0.0),
                'timestamp': timestamp,
                'device_id': device_id,
                'latency': result.get('total_latency', 0),
                'cache_hit': result.get('cache_hit', False),
                'hand_detected': result.get('hand_detected', False)
            })
        }
        
    except Exception as e:
        logger.error(f"Error in optimized processing: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'error': f'Processing error: {str(e)}',
                'latency': time.time() - start_time
            })
        }

def process_with_bedrock(frame_data: str) -> Dict[str, Any]:
    """
    Process frame with Bedrock using optimized prompt
    """
    try:
        # Get optimized prompt
        prompt = pipeline.optimize_prompt({'estimated_size_bytes': len(frame_data) * 3 // 4})
        
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
        
        # Call Bedrock
        response = bedrock_client.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
            body=json.dumps(request_body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        content = response_body['content'][0]['text']
        
        # Try to parse as JSON
        try:
            bedrock_result = json.loads(content)
        except json.JSONDecodeError:
            # Fallback parsing
            bedrock_result = {
                "translation": content[:100],
                "confidence": 0.5,
                "hand_detected": "hand" in content.lower()
            }
        
        return bedrock_result
        
    except Exception as e:
        logger.error(f"Bedrock processing error: {str(e)}")
        return {
            "translation": "Bedrock processing failed",
            "confidence": 0.0,
            "hand_detected": False,
            "error": str(e)
        }

def store_result_in_s3(device_id: str, timestamp: str, result: Dict[str, Any]) -> None:
    """
    Store processing result in S3 with performance metrics
    """
    try:
        bucket_name = os.environ.get('DATA_BUCKET')
        if not bucket_name:
            return
        
        # Create enriched result for storage
        storage_result = {
            **result,
            'stored_at': time.time(),
            'performance_stats': pipeline.get_performance_stats()
        }
        
        key = f"results/{device_id}/{timestamp}.json"
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=json.dumps(storage_result, default=str),
            ContentType='application/json'
        )
        
    except Exception as e:
        logger.error(f"S3 storage error: {str(e)}")

def get_cors_headers() -> Dict[str, str]:
    """Get CORS headers for API responses"""
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }

def get_performance_metrics(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Endpoint to get current performance metrics
    """
    try:
        stats = pipeline.get_performance_stats()
        cleanup_result = pipeline.cleanup()
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'performance_stats': stats,
                'cleanup_result': cleanup_result,
                'timestamp': time.time()
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': str(e)})
        }

# Main handler - delegate to optimized version
def process_sign(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    return process_sign_optimized(event, context)