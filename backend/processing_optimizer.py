#!/usr/bin/env python3
"""
Processing pipeline optimizations for real-time sign language interpretation
"""

import time
import hashlib
import base64
import json
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class ProcessingMetrics:
    """Metrics for processing performance"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_latency: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0

class FrameCache:
    """Simple frame caching to avoid reprocessing identical frames"""
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 30):
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        self.max_size = max_size
        self.ttl = timedelta(seconds=ttl_seconds)
    
    def _generate_key(self, frame_data: str) -> str:
        """Generate cache key from frame data"""
        # Use first and last 100 characters + length for faster hashing
        sample = frame_data[:100] + frame_data[-100:] + str(len(frame_data))
        return hashlib.md5(sample.encode()).hexdigest()
    
    def get(self, frame_data: str) -> Optional[Any]:
        """Get cached result if available and not expired"""
        key = self._generate_key(frame_data)
        
        if key in self.cache:
            result, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return result
            else:
                # Remove expired entry
                del self.cache[key]
        
        return None
    
    def put(self, frame_data: str, result: Any) -> None:
        """Cache processing result"""
        key = self._generate_key(frame_data)
        
        # Remove oldest entries if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        self.cache[key] = (result, datetime.now())
    
    def clear_expired(self) -> int:
        """Remove expired entries and return count removed"""
        now = datetime.now()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if now - timestamp >= self.ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)

class RateLimiter:
    """Rate limiting for processing requests"""
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = timedelta(seconds=window_seconds)
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for client"""
        now = datetime.now()
        
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Remove old requests outside window
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < self.window
        ]
        
        # Check if under limit
        if len(self.requests[client_id]) < self.max_requests:
            self.requests[client_id].append(now)
            return True
        
        return False

class ProcessingPipeline:
    """Optimized processing pipeline for real-time sign language interpretation"""
    
    def __init__(self):
        self.cache = FrameCache(max_size=50, ttl_seconds=20)
        self.rate_limiter = RateLimiter(max_requests=20, window_seconds=60)
        self.metrics = ProcessingMetrics()
    
    def preprocess_frame(self, frame_data: str) -> Tuple[str, Dict[str, Any]]:
        """Preprocess frame data for optimal AI processing"""
        start_time = time.time()
        
        # Basic validation
        if not frame_data or len(frame_data) < 100:
            raise ValueError("Invalid frame data: too small or empty")
        
        # Decode and analyze frame
        try:
            # Quick size check (base64 encoded)
            estimated_bytes = len(frame_data) * 3 // 4
            
            metadata = {
                'estimated_size_bytes': estimated_bytes,
                'base64_length': len(frame_data),
                'preprocessing_time': time.time() - start_time
            }
            
            # For very large images, we might want to resize
            # This is a placeholder for actual image processing
            if estimated_bytes > 500000:  # > 500KB
                metadata['size_warning'] = True
            
            return frame_data, metadata
            
        except Exception as e:
            raise ValueError(f"Frame preprocessing failed: {e}")
    
    def optimize_prompt(self, frame_metadata: Dict[str, Any]) -> str:
        """Generate optimized prompt based on frame characteristics"""
        
        base_prompt = """
        Analyze this image for American Sign Language (ASL) signs. Be concise and accurate.
        
        Focus on:
        1. Hand positions and finger configurations
        2. Common ASL signs (A-Z, common words)
        3. Movement patterns if detectable
        
        Respond in JSON format:
        {
            "translation": "detected sign or 'No clear signs'",
            "confidence": 0.0-1.0,
            "hand_detected": true/false
        }
        """
        
        # Adjust prompt based on image characteristics
        if frame_metadata.get('size_warning'):
            base_prompt += "\nNote: Large image - focus on central region."
        
        return base_prompt.strip()
    
    def process_with_cache(self, frame_data: str, client_id: str = "default") -> Dict[str, Any]:
        """Process frame with caching and rate limiting"""
        start_time = time.time()
        
        try:
            # Increment total requests
            self.metrics.total_requests += 1
            
            # Check rate limiting
            if not self.rate_limiter.is_allowed(client_id):
                return {
                    'translation': 'Rate limit exceeded',
                    'confidence': 0.0,
                    'error': 'Too many requests',
                    'latency': time.time() - start_time
                }
            
            # Check cache first
            cached_result = self.cache.get(frame_data)
            if cached_result:
                self.metrics.cache_hits += 1
                cached_result['cache_hit'] = True
                cached_result['latency'] = time.time() - start_time
                return cached_result
            
            self.metrics.cache_misses += 1
            
            # Preprocess frame
            processed_frame, metadata = self.preprocess_frame(frame_data)
            
            # Simulate AI processing (replace with actual Bedrock call)
            # This is where the real Bedrock processing would happen
            processing_time = time.time()
            
            # Mock result for testing
            result = {
                'translation': 'Sample sign detected',
                'confidence': 0.75,
                'hand_detected': True,
                'processing_metadata': metadata,
                'cache_hit': False,
                'processing_time': time.time() - processing_time,
                'latency': time.time() - start_time
            }
            
            # Cache the result
            self.cache.put(frame_data, result.copy())
            
            # Update metrics
            self.metrics.successful_requests += 1
            self.update_average_latency(time.time() - start_time)
            
            return result
            
        except Exception as e:
            self.metrics.failed_requests += 1
            return {
                'translation': 'Processing error',
                'confidence': 0.0,
                'error': str(e),
                'latency': time.time() - start_time
            }
    
    def update_average_latency(self, latency: float) -> None:
        """Update rolling average latency"""
        if self.metrics.successful_requests == 1:
            self.metrics.average_latency = latency
        else:
            # Simple moving average
            alpha = 0.1  # Weight for new measurement
            self.metrics.average_latency = (
                alpha * latency + (1 - alpha) * self.metrics.average_latency
            )
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        total = self.metrics.total_requests
        
        if total == 0:
            return {
                'status': 'No requests processed yet'
            }
        
        cache_total = self.metrics.cache_hits + self.metrics.cache_misses
        cache_hit_rate = (
            self.metrics.cache_hits / cache_total * 100 
            if cache_total > 0 else 0
        )
        
        return {
            'total_requests': total,
            'success_rate': f"{self.metrics.successful_requests / total * 100:.1f}%",
            'failure_rate': f"{self.metrics.failed_requests / total * 100:.1f}%",
            'average_latency': f"{self.metrics.average_latency:.3f}s",
            'cache_hit_rate': f"{cache_hit_rate:.1f}%",
            'cache_size': len(self.cache.cache),
            'active_clients': len(self.rate_limiter.requests)
        }
    
    def cleanup(self) -> None:
        """Cleanup expired cache entries"""
        expired_count = self.cache.clear_expired()
        return {'expired_entries_removed': expired_count}

# Global pipeline instance
pipeline = ProcessingPipeline()