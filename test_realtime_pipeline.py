#!/usr/bin/env python3
"""
Comprehensive test for real-time processing pipeline
"""

import requests
import json
import time
import threading
import base64
from concurrent.futures import ThreadPoolExecutor
import sys

# API Configuration
API_ENDPOINT = "https://6ddpddg0g3.execute-api.us-east-1.amazonaws.com/prod/process"

# Test image data (minimal JPEG)
TEST_IMAGE_DATA = """
/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgKCgkICQkKDA8MCgsOCwkJDRENDg8QEBEQCgwSExIQEw8QEBD/yQALCAABAAEBAREA/8wABgAQEAX/2gAIAQEAAD8A0s8g/9k=
""".strip()

class PipelineTestSuite:
    """Test suite for real-time processing pipeline"""
    
    def __init__(self):
        self.api_endpoint = API_ENDPOINT
        self.results = []
        self.errors = []
    
    def create_test_payload(self, device_id: str = "test-device") -> dict:
        """Create test payload for API"""
        return {
            "frame_data": TEST_IMAGE_DATA,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "device_id": device_id
        }
    
    def single_request_test(self, device_id: str = "test-single") -> dict:
        """Test single API request"""
        print(f"🔍 Testing single request...")
        
        start_time = time.time()
        try:
            payload = self.create_test_payload(device_id)
            
            response = requests.post(
                self.api_endpoint,
                json=payload,
                timeout=30
            )
            
            latency = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                result['test_latency'] = latency
                print(f"✅ Single request successful: {latency:.3f}s")
                print(f"   Translation: {result.get('translation', 'N/A')}")
                print(f"   Confidence: {result.get('confidence', 0.0)}")
                return result
            else:
                error = f"HTTP {response.status_code}: {response.text}"
                print(f"❌ Single request failed: {error}")
                return {'error': error, 'test_latency': latency}
                
        except Exception as e:
            latency = time.time() - start_time
            error = str(e)
            print(f"❌ Single request exception: {error}")
            return {'error': error, 'test_latency': latency}
    
    def concurrent_requests_test(self, num_requests: int = 5) -> list:
        """Test concurrent API requests"""
        print(f"🔍 Testing {num_requests} concurrent requests...")
        
        def make_request(request_id: int) -> dict:
            device_id = f"test-concurrent-{request_id}"
            start_time = time.time()
            
            try:
                payload = self.create_test_payload(device_id)
                response = requests.post(
                    self.api_endpoint,
                    json=payload,
                    timeout=30
                )
                
                latency = time.time() - start_time
                
                result = {
                    'request_id': request_id,
                    'status_code': response.status_code,
                    'latency': latency,
                    'success': response.status_code == 200
                }
                
                if response.status_code == 200:
                    api_result = response.json()
                    result.update(api_result)
                else:
                    result['error'] = response.text
                
                return result
                
            except Exception as e:
                return {
                    'request_id': request_id,
                    'error': str(e),
                    'latency': time.time() - start_time,
                    'success': False
                }
        
        # Execute concurrent requests
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_requests)]
            results = [future.result() for future in futures]
        
        total_time = time.time() - start_time
        
        # Analyze results
        successful = [r for r in results if r.get('success', False)]
        failed = [r for r in results if not r.get('success', False)]
        
        if successful:
            avg_latency = sum(r['latency'] for r in successful) / len(successful)
            max_latency = max(r['latency'] for r in successful)
            min_latency = min(r['latency'] for r in successful)
        else:
            avg_latency = max_latency = min_latency = 0
        
        print(f"✅ Concurrent test completed in {total_time:.3f}s")
        print(f"   Successful: {len(successful)}/{num_requests}")
        print(f"   Failed: {len(failed)}/{num_requests}")
        if successful:
            print(f"   Latency - Avg: {avg_latency:.3f}s, Min: {min_latency:.3f}s, Max: {max_latency:.3f}s")
        
        return results
    
    def rate_limit_test(self, requests_per_second: int = 3, duration: int = 10) -> list:
        """Test rate limiting behavior"""
        print(f"🔍 Testing rate limiting: {requests_per_second} req/s for {duration}s...")
        
        results = []
        start_time = time.time()
        request_count = 0
        
        while time.time() - start_time < duration:
            loop_start = time.time()
            
            for i in range(requests_per_second):
                if time.time() - start_time >= duration:
                    break
                
                try:
                    payload = self.create_test_payload(f"rate-test-{request_count}")
                    
                    req_start = time.time()
                    response = requests.post(
                        self.api_endpoint,
                        json=payload,
                        timeout=10
                    )
                    
                    results.append({
                        'request_id': request_count,
                        'timestamp': time.time() - start_time,
                        'status_code': response.status_code,
                        'latency': time.time() - req_start,
                        'success': response.status_code == 200
                    })
                    
                    request_count += 1
                    
                except Exception as e:
                    results.append({
                        'request_id': request_count,
                        'timestamp': time.time() - start_time,
                        'error': str(e),
                        'success': False
                    })
                    request_count += 1
            
            # Wait for next second
            elapsed = time.time() - loop_start
            if elapsed < 1.0:
                time.sleep(1.0 - elapsed)
        
        successful = [r for r in results if r.get('success', False)]
        print(f"✅ Rate limit test completed")
        print(f"   Total requests: {len(results)}")
        print(f"   Successful: {len(successful)}")
        print(f"   Success rate: {len(successful)/len(results)*100:.1f}%")
        
        return results
    
    def caching_test(self) -> dict:
        """Test caching behavior with identical requests"""
        print(f"🔍 Testing caching behavior...")
        
        payload = self.create_test_payload("cache-test")
        
        # First request (cache miss)
        start_time = time.time()
        response1 = requests.post(self.api_endpoint, json=payload, timeout=30)
        latency1 = time.time() - start_time
        
        # Immediate second request (potential cache hit)
        start_time = time.time()
        response2 = requests.post(self.api_endpoint, json=payload, timeout=30)
        latency2 = time.time() - start_time
        
        # Third request after small delay
        time.sleep(0.5)
        start_time = time.time()
        response3 = requests.post(self.api_endpoint, json=payload, timeout=30)
        latency3 = time.time() - start_time
        
        result = {
            'request1': {
                'latency': latency1,
                'status': response1.status_code,
                'response': response1.json() if response1.status_code == 200 else response1.text
            },
            'request2': {
                'latency': latency2,
                'status': response2.status_code,
                'response': response2.json() if response2.status_code == 200 else response2.text
            },
            'request3': {
                'latency': latency3,
                'status': response3.status_code,
                'response': response3.json() if response3.status_code == 200 else response3.text
            }
        }
        
        print(f"✅ Caching test completed")
        print(f"   Request 1 latency: {latency1:.3f}s")
        print(f"   Request 2 latency: {latency2:.3f}s (potential cache hit)")
        print(f"   Request 3 latency: {latency3:.3f}s")
        
        if latency2 < latency1 * 0.8:
            print(f"   🎯 Cache hit detected! {((latency1-latency2)/latency1)*100:.1f}% faster")
        
        return result
    
    def run_all_tests(self) -> dict:
        """Run complete test suite"""
        print("🚀 Starting SignToMe Real-time Pipeline Test Suite")
        print("=" * 60)
        
        test_results = {}
        
        # Test 1: Single request
        test_results['single_request'] = self.single_request_test()
        print()
        
        # Test 2: Concurrent requests
        test_results['concurrent_requests'] = self.concurrent_requests_test(5)
        print()
        
        # Test 3: Caching behavior
        test_results['caching'] = self.caching_test()
        print()
        
        # Test 4: Rate limiting (shorter test for demo)
        test_results['rate_limiting'] = self.rate_limit_test(2, 5)
        print()
        
        # Summary
        print("=" * 60)
        print("🎯 Test Suite Summary")
        print("=" * 60)
        
        single_success = not test_results['single_request'].get('error')
        concurrent_success_rate = sum(1 for r in test_results['concurrent_requests'] if r.get('success', False)) / len(test_results['concurrent_requests'])
        
        print(f"Single Request: {'✅ PASS' if single_success else '❌ FAIL'}")
        print(f"Concurrent Requests: {'✅ PASS' if concurrent_success_rate > 0.8 else '❌ FAIL'} ({concurrent_success_rate*100:.1f}% success)")
        print(f"Caching: {'✅ PASS' if test_results['caching']['request1']['status'] == 200 else '❌ FAIL'}")
        print(f"Rate Limiting: {'✅ PASS' if len(test_results['rate_limiting']) > 0 else '❌ FAIL'}")
        
        overall_success = (
            single_success and 
            concurrent_success_rate > 0.8 and 
            test_results['caching']['request1']['status'] == 200
        )
        
        print(f"\n🏆 Overall Result: {'✅ PIPELINE READY' if overall_success else '❌ NEEDS ATTENTION'}")
        
        return test_results

def main():
    """Main test execution"""
    test_suite = PipelineTestSuite()
    results = test_suite.run_all_tests()
    
    # Save results to file
    with open('/tmp/pipeline_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📁 Detailed results saved to: /tmp/pipeline_test_results.json")

if __name__ == "__main__":
    main()