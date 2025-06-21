# SignToMe API Reference

**Version**: 1.0.0  
**Base URL**: `https://6ddpddg0g3.execute-api.us-east-1.amazonaws.com/prod`

## Overview

The SignToMe API provides real-time sign language interpretation services using AWS Bedrock AI. The API accepts video frame data and returns interpreted text with confidence scores.

## Authentication

Currently, the API is open for demonstration purposes. Production deployment would include:
- API key authentication
- JWT token validation
- Rate limiting per authenticated user

## Base URL and Endpoints

| Environment | Base URL |
|-------------|----------|
| Production | `https://6ddpddg0g3.execute-api.us-east-1.amazonaws.com/prod` |
| Development | `http://localhost:3001/api` |

---

## Endpoints

### Process Sign Language Frame

**Endpoint**: `POST /process`

Processes a single video frame and returns sign language interpretation.

#### Request

**Headers**:
```
Content-Type: application/json
```

**Body**:
```json
{
  "frame_data": "string",      // Required: Base64-encoded JPEG image
  "timestamp": "string",       // Required: ISO 8601 timestamp
  "device_id": "string"        // Required: Unique device identifier
}
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `frame_data` | string | Yes | Base64-encoded JPEG image data (max 10MB) |
| `timestamp` | string | Yes | ISO 8601 timestamp (e.g., "2025-06-21T12:00:00Z") |
| `device_id` | string | Yes | Unique identifier for the requesting device |

#### Response

**Success Response** (200 OK):
```json
{
  "translation": "Hello",
  "confidence": 0.85,
  "timestamp": "2025-06-21T12:00:00Z",
  "device_id": "web-interface"
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `translation` | string | Interpreted sign language text |
| `confidence` | number | Confidence score (0.0-1.0) |
| `timestamp` | string | Original request timestamp |
| `device_id` | string | Original device identifier |

#### Error Responses

**400 Bad Request**:
```json
{
  "error": "No frame data provided"
}
```

**413 Payload Too Large**:
```json
{
  "error": "Frame data exceeds maximum size limit"
}
```

**429 Too Many Requests**:
```json
{
  "error": "Rate limit exceeded"
}
```

**500 Internal Server Error**:
```json
{
  "error": "Processing error: Internal server error"
}
```

#### Example Usage

**cURL**:
```bash
curl -X POST https://6ddpddg0g3.execute-api.us-east-1.amazonaws.com/prod/process \
  -H "Content-Type: application/json" \
  -d '{
    "frame_data": "/9j/4AAQSkZJRgABAQEA...",
    "timestamp": "2025-06-21T12:00:00Z",
    "device_id": "demo-device"
  }'
```

**JavaScript**:
```javascript
const response = await fetch('/api/process', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    frame_data: base64ImageData,
    timestamp: new Date().toISOString(),
    device_id: 'web-interface'
  })
});

const result = await response.json();
console.log('Translation:', result.translation);
```

**Python**:
```python
import requests
import base64

def process_sign_frame(image_path):
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    response = requests.post(
        'https://6ddpddg0g3.execute-api.us-east-1.amazonaws.com/prod/process',
        json={
            'frame_data': image_data,
            'timestamp': '2025-06-21T12:00:00Z',
            'device_id': 'python-client'
        }
    )
    
    return response.json()
```

---

## Rate Limiting

### Current Limits

| Limit Type | Value | Window |
|------------|-------|--------|
| Requests per device | 20 | 1 minute |
| Concurrent requests | 100 | Global |
| Maximum payload size | 10 MB | Per request |

### Rate Limit Headers

The API includes rate limiting information in response headers:

```
X-RateLimit-Limit: 20
X-RateLimit-Remaining: 15
X-RateLimit-Reset: 1640995200
```

### Rate Limit Response

When rate limits are exceeded:

**Status**: `429 Too Many Requests`
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60
}
```

---

## Image Requirements

### Supported Formats
- **JPEG** (recommended)
- **PNG** (converted to JPEG)

### Optimal Specifications
- **Resolution**: 640x480 pixels
- **Quality**: 85% JPEG compression
- **Size**: 50KB - 500KB
- **Aspect Ratio**: 4:3 or 16:9

### Image Guidelines
- **Lighting**: Well-lit environment with good contrast
- **Background**: Solid, contrasting background preferred
- **Hand Position**: Clearly visible hands within frame
- **Angle**: Frontal view of signer

---

## Response Format

### Success Response Structure

```json
{
  "translation": "string",     // Interpreted text
  "confidence": "number",      // 0.0 to 1.0
  "timestamp": "string",       // ISO 8601 timestamp
  "device_id": "string",       // Device identifier
  "processing_time": "number", // Optional: processing duration in ms
  "cache_hit": "boolean"       // Optional: whether result was cached
}
```

### Error Response Structure

```json
{
  "error": "string",           // Error message
  "error_code": "string",      // Optional: error code
  "details": "object"          // Optional: additional error details
}
```

### Confidence Score Interpretation

| Range | Interpretation | Action |
|-------|---------------|--------|
| 0.8 - 1.0 | High confidence | Display result prominently |
| 0.5 - 0.79 | Medium confidence | Display with qualification |
| 0.2 - 0.49 | Low confidence | Suggest retry or improvement |
| 0.0 - 0.19 | Very low confidence | Indicate unclear sign |

---

## Error Handling

### Error Types

#### Client Errors (4xx)

**400 Bad Request**:
- Missing required fields
- Invalid timestamp format
- Empty frame data

**413 Payload Too Large**:
- Image data exceeds 10MB limit
- Request body too large

**422 Unprocessable Entity**:
- Invalid base64 encoding
- Corrupted image data
- Unsupported image format

**429 Too Many Requests**:
- Rate limit exceeded
- Too many concurrent requests

#### Server Errors (5xx)

**500 Internal Server Error**:
- AI processing failure
- Database connection error
- Unexpected server error

**503 Service Unavailable**:
- Bedrock service unavailable
- Temporary maintenance

**504 Gateway Timeout**:
- Processing timeout (>30 seconds)
- Network connectivity issues

### Error Response Examples

**Invalid Input**:
```json
{
  "error": "Invalid frame data format",
  "error_code": "INVALID_INPUT",
  "details": {
    "field": "frame_data",
    "reason": "Not valid base64 encoding"
  }
}
```

**Processing Failure**:
```json
{
  "error": "AI processing failed",
  "error_code": "PROCESSING_ERROR",
  "details": {
    "retry_able": true,
    "estimated_retry_delay": 5000
  }
}
```

---

## Performance Considerations

### Latency Optimization

**Typical Response Times**:
- **Cache Hit**: 100-300ms
- **Cold Start**: 500-1000ms
- **Warm Lambda**: 800-2000ms
- **Peak Load**: 2000-5000ms

**Optimization Strategies**:
1. **Image Compression**: Use 85% JPEG quality
2. **Batch Processing**: Group multiple frames when possible
3. **Caching**: Leverage automatic result caching
4. **Retry Logic**: Implement exponential backoff

### Best Practices

#### Client Implementation

```javascript
class SignToMeClient {
  constructor(apiEndpoint) {
    this.endpoint = apiEndpoint;
    this.rateLimiter = new RateLimiter(20, 60000); // 20 req/min
  }
  
  async processFrame(frameData, deviceId) {
    // Check rate limit
    if (!this.rateLimiter.tryAcquire()) {
      throw new Error('Rate limit exceeded');
    }
    
    // Optimize image
    const optimizedFrame = await this.optimizeImage(frameData);
    
    // Make request with retry
    return this.makeRequestWithRetry({
      frame_data: optimizedFrame,
      timestamp: new Date().toISOString(),
      device_id: deviceId
    });
  }
  
  async makeRequestWithRetry(payload, maxRetries = 3) {
    for (let i = 0; i < maxRetries; i++) {
      try {
        const response = await fetch(this.endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
          timeout: 30000
        });
        
        if (response.ok) {
          return await response.json();
        } else if (response.status >= 500 && i < maxRetries - 1) {
          // Retry on server errors
          await this.delay(Math.pow(2, i) * 1000);
          continue;
        } else {
          throw new Error(`HTTP ${response.status}`);
        }
      } catch (error) {
        if (i === maxRetries - 1) throw error;
        await this.delay(Math.pow(2, i) * 1000);
      }
    }
  }
}
```

---

## SDK Examples

### JavaScript/TypeScript SDK

```typescript
interface SignToMeConfig {
  apiEndpoint: string;
  deviceId: string;
  timeout?: number;
}

interface ProcessResult {
  translation: string;
  confidence: number;
  timestamp: string;
  device_id: string;
}

class SignToMeSDK {
  constructor(private config: SignToMeConfig) {}
  
  async processFrame(frameData: string): Promise<ProcessResult> {
    const response = await fetch(`${this.config.apiEndpoint}/process`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        frame_data: frameData,
        timestamp: new Date().toISOString(),
        device_id: this.config.deviceId
      }),
      signal: AbortSignal.timeout(this.config.timeout || 30000)
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    
    return await response.json();
  }
}
```

### Python SDK

```python
import requests
import base64
from typing import Dict, Any
from datetime import datetime

class SignToMeClient:
    def __init__(self, api_endpoint: str, device_id: str):
        self.api_endpoint = api_endpoint
        self.device_id = device_id
        self.session = requests.Session()
    
    def process_frame(self, image_path: str) -> Dict[str, Any]:
        """Process image file for sign language interpretation."""
        with open(image_path, 'rb') as f:
            frame_data = base64.b64encode(f.read()).decode('utf-8')
        
        return self.process_frame_data(frame_data)
    
    def process_frame_data(self, frame_data: str) -> Dict[str, Any]:
        """Process base64 frame data."""
        payload = {
            'frame_data': frame_data,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'device_id': self.device_id
        }
        
        response = self.session.post(
            f'{self.api_endpoint}/process',
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()
```

---

## Webhook Support (Future)

### Webhook Configuration

```json
{
  "webhook_url": "https://your-app.com/webhook",
  "events": ["processing_complete", "error_occurred"],
  "secret": "webhook-secret-key"
}
```

### Webhook Payload

```json
{
  "event": "processing_complete",
  "timestamp": "2025-06-21T12:00:00Z",
  "data": {
    "request_id": "req_123456",
    "device_id": "device_001",
    "result": {
      "translation": "Hello",
      "confidence": 0.85
    }
  }
}
```

---

## Changelog

### Version 1.0.0 (2025-06-21)
- Initial API release
- Basic sign language processing
- Rate limiting implementation
- Error handling and validation

### Planned Features
- WebSocket real-time streaming
- Batch processing endpoint
- Webhook support
- Enhanced authentication
- Multi-language sign language support

---

## Support

For API support and questions:
- **Documentation**: [Technical Specification](./TECHNICAL_SPECIFICATION.md)
- **Demo**: http://localhost:3001
- **Repository**: [GitHub Repository URL]

For AWS Breaking Barriers Hackathon 2025 submission.