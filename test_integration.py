#!/usr/bin/env python3
"""
Integration testing for SignToMe end-to-end system
"""

import requests
import json
import time
import base64
import io
from PIL import Image, ImageDraw, ImageFont
import sys
import subprocess
import threading
from typing import List, Dict, Any

class SignToMeIntegrationTest:
    """Comprehensive integration test suite"""
    
    def __init__(self):
        self.api_endpoint = "https://6ddpddg0g3.execute-api.us-east-1.amazonaws.com/prod/process"
        self.frontend_url = "http://localhost:3000"
        self.test_results = {}
        self.issues_found = []
        
    def create_realistic_sign_image(self, sign_text: str = "HELLO") -> str:
        """Create a realistic ASL sign image for testing"""
        # Create 640x480 image
        img = Image.new('RGB', (640, 480), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # Draw background
        draw.rectangle([0, 0, 640, 480], fill='lightblue')
        
        # Draw person silhouette
        draw.ellipse([200, 100, 440, 340], fill='peachpuff', outline='darkgray', width=2)
        
        # Draw hand for sign
        if sign_text == "HELLO":
            # HELLO sign - hand near forehead moving outward
            hand_x, hand_y = 150, 80
            # Palm
            draw.ellipse([hand_x, hand_y, hand_x+80, hand_y+100], fill='peachpuff', outline='black', width=2)
            # Fingers
            for i, finger_pos in enumerate([(hand_x+15, hand_y-40), (hand_x+35, hand_y-45), 
                                           (hand_x+55, hand_y-40), (hand_x+75, hand_y-35)]):
                draw.ellipse([finger_pos[0]-8, finger_pos[1]-25, finger_pos[0]+8, finger_pos[1]+15], 
                            fill='peachpuff', outline='black', width=1)
            # Motion lines
            for i in range(3):
                start_x = hand_x + 90 + (i * 15)
                draw.line([start_x, hand_y+30, start_x+20, hand_y+35], fill='gray', width=2)
                
        elif sign_text == "THANK YOU":
            # THANK YOU sign - fingers to chin then out
            hand_x, hand_y = 280, 220
            draw.ellipse([hand_x, hand_y, hand_x+60, hand_y+80], fill='peachpuff', outline='black', width=2)
            # Motion arc
            draw.arc([hand_x+30, hand_y-20, hand_x+120, hand_y+70], 45, 135, fill='gray', width=3)
            
        elif sign_text == "PLEASE":
            # PLEASE sign - flat hand on chest, circular motion
            hand_x, hand_y = 290, 250
            draw.ellipse([hand_x, hand_y, hand_x+70, hand_y+60], fill='peachpuff', outline='black', width=2)
            # Circular motion indicator
            draw.ellipse([hand_x+10, hand_y+10, hand_x+50, hand_y+50], outline='gray', width=2, fill=None)
        
        # Add text label
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        except:
            font = ImageFont.load_default()
            
        draw.text((50, 400), f"ASL Sign: {sign_text}", fill='darkblue', font=font)
        draw.text((50, 430), "SignToMe Integration Test", fill='gray', font=font)
        
        # Convert to base64
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    def test_api_endpoints(self) -> Dict[str, Any]:
        """Test all API endpoints"""
        print("🔍 Testing API endpoints...")
        
        results = {}
        
        # Test main processing endpoint
        test_signs = ["HELLO", "THANK YOU", "PLEASE"]
        
        for sign in test_signs:
            print(f"  Testing {sign} sign...")
            
            image_data = self.create_realistic_sign_image(sign)
            payload = {
                "frame_data": image_data,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "device_id": f"integration-test-{sign.lower()}"
            }
            
            start_time = time.time()
            try:
                response = requests.post(
                    self.api_endpoint,
                    json=payload,
                    timeout=30,
                    headers={"Content-Type": "application/json"}
                )
                
                latency = time.time() - start_time
                
                if response.status_code == 200:
                    api_result = response.json()
                    results[sign] = {
                        "success": True,
                        "latency": latency,
                        "translation": api_result.get("translation", ""),
                        "confidence": api_result.get("confidence", 0.0),
                        "response": api_result
                    }
                    print(f"    ✅ {sign}: {api_result.get('translation', 'N/A')} ({latency:.2f}s)")
                else:
                    results[sign] = {
                        "success": False,
                        "error": f"HTTP {response.status_code}: {response.text}",
                        "latency": latency
                    }
                    print(f"    ❌ {sign}: HTTP {response.status_code}")
                    self.issues_found.append(f"API error for {sign}: HTTP {response.status_code}")
                    
            except Exception as e:
                results[sign] = {
                    "success": False,
                    "error": str(e),
                    "latency": time.time() - start_time
                }
                print(f"    ❌ {sign}: {str(e)}")
                self.issues_found.append(f"API exception for {sign}: {str(e)}")
        
        return results
    
    def test_frontend_connectivity(self) -> Dict[str, Any]:
        """Test frontend server connectivity"""
        print("🔍 Testing frontend connectivity...")
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            
            if response.status_code == 200:
                print("  ✅ Frontend server is accessible")
                
                # Check for key components in HTML
                html_content = response.text
                has_camera_button = "Start Camera" in html_content or "camera" in html_content.lower()
                has_video_element = "<video" in html_content
                has_signme_title = "SignToMe" in html_content
                
                return {
                    "accessible": True,
                    "status_code": response.status_code,
                    "has_camera_button": has_camera_button,
                    "has_video_element": has_video_element,
                    "has_title": has_signme_title,
                    "content_length": len(html_content)
                }
            else:
                print(f"  ❌ Frontend returned HTTP {response.status_code}")
                self.issues_found.append(f"Frontend HTTP error: {response.status_code}")
                return {
                    "accessible": False,
                    "status_code": response.status_code,
                    "error": f"HTTP {response.status_code}"
                }
                
        except requests.exceptions.ConnectionError:
            print("  ❌ Frontend server not running")
            self.issues_found.append("Frontend server not accessible - run 'npm run dev' in frontend directory")
            return {
                "accessible": False,
                "error": "Connection refused - server not running"
            }
        except Exception as e:
            print(f"  ❌ Frontend test error: {str(e)}")
            self.issues_found.append(f"Frontend test exception: {str(e)}")
            return {
                "accessible": False,
                "error": str(e)
            }
    
    def test_aws_services(self) -> Dict[str, Any]:
        """Test AWS service connectivity"""
        print("🔍 Testing AWS services...")
        
        results = {}
        
        # Test Lambda function directly
        try:
            import boto3
            
            # Test S3 bucket access
            try:
                s3_client = boto3.client('s3', region_name='us-east-1')
                buckets = s3_client.list_buckets()
                
                signtome_buckets = [b['Name'] for b in buckets['Buckets'] if 'signtome' in b['Name']]
                
                results['s3'] = {
                    "accessible": True,
                    "signtome_buckets": signtome_buckets,
                    "total_buckets": len(buckets['Buckets'])
                }
                print(f"  ✅ S3 accessible ({len(signtome_buckets)} SignToMe buckets found)")
                
            except Exception as e:
                results['s3'] = {"accessible": False, "error": str(e)}
                print(f"  ❌ S3 error: {str(e)}")
                self.issues_found.append(f"S3 access error: {str(e)}")
            
            # Test CloudFormation stack
            try:
                cf_client = boto3.client('cloudformation', region_name='us-east-1')
                stacks = cf_client.describe_stacks(StackName='SignToMeStack')
                
                stack = stacks['Stacks'][0]
                stack_status = stack['StackStatus']
                
                results['cloudformation'] = {
                    "accessible": True,
                    "stack_status": stack_status,
                    "stack_name": stack['StackName'],
                    "creation_time": str(stack['CreationTime'])
                }
                
                if stack_status in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
                    print(f"  ✅ CloudFormation stack: {stack_status}")
                else:
                    print(f"  ⚠️  CloudFormation stack: {stack_status}")
                    self.issues_found.append(f"CloudFormation stack not in optimal state: {stack_status}")
                    
            except Exception as e:
                results['cloudformation'] = {"accessible": False, "error": str(e)}
                print(f"  ❌ CloudFormation error: {str(e)}")
                self.issues_found.append(f"CloudFormation access error: {str(e)}")
                
        except ImportError:
            results['boto3'] = {"accessible": False, "error": "boto3 not available"}
            print("  ⚠️  boto3 not available for direct AWS testing")
        
        return results
    
    def test_performance_benchmarks(self) -> Dict[str, Any]:
        """Test performance benchmarks"""
        print("🔍 Testing performance benchmarks...")
        
        # Test multiple requests for performance
        num_requests = 5
        latencies = []
        successes = 0
        
        test_image = self.create_realistic_sign_image("HELLO")
        
        for i in range(num_requests):
            payload = {
                "frame_data": test_image,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "device_id": f"perf-test-{i}"
            }
            
            start_time = time.time()
            try:
                response = requests.post(self.api_endpoint, json=payload, timeout=30)
                latency = time.time() - start_time
                latencies.append(latency)
                
                if response.status_code == 200:
                    successes += 1
                    
            except Exception as e:
                latencies.append(30.0)  # Timeout value
                
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        min_latency = min(latencies)
        success_rate = successes / num_requests
        
        # Performance thresholds
        performance_grade = "A"
        if avg_latency > 3.0:
            performance_grade = "C"
            self.issues_found.append(f"High average latency: {avg_latency:.2f}s")
        elif avg_latency > 2.0:
            performance_grade = "B"
        
        if success_rate < 0.8:
            self.issues_found.append(f"Low success rate: {success_rate*100:.1f}%")
        
        results = {
            "num_requests": num_requests,
            "successes": successes,
            "success_rate": success_rate,
            "avg_latency": avg_latency,
            "min_latency": min_latency,
            "max_latency": max_latency,
            "performance_grade": performance_grade,
            "latencies": latencies
        }
        
        print(f"  📊 Performance Results:")
        print(f"    Success Rate: {success_rate*100:.1f}%")
        print(f"    Avg Latency: {avg_latency:.2f}s")
        print(f"    Grade: {performance_grade}")
        
        return results
    
    def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling scenarios"""
        print("🔍 Testing error handling...")
        
        test_cases = [
            {
                "name": "Empty payload",
                "payload": {},
                "expected_status": 400
            },
            {
                "name": "Missing frame_data",
                "payload": {"timestamp": "2025-06-21T12:00:00Z", "device_id": "test"},
                "expected_status": 400
            },
            {
                "name": "Invalid base64",
                "payload": {
                    "frame_data": "invalid_base64_data",
                    "timestamp": "2025-06-21T12:00:00Z",
                    "device_id": "test"
                },
                "expected_status": [400, 500]  # Could be either
            },
            {
                "name": "Very large payload",
                "payload": {
                    "frame_data": "A" * 1000000,  # 1MB of data
                    "timestamp": "2025-06-21T12:00:00Z",
                    "device_id": "test"
                },
                "expected_status": [400, 413, 500]
            }
        ]
        
        results = {}
        
        for test_case in test_cases:
            print(f"  Testing: {test_case['name']}")
            
            try:
                response = requests.post(
                    self.api_endpoint,
                    json=test_case['payload'],
                    timeout=30
                )
                
                expected = test_case['expected_status']
                if isinstance(expected, list):
                    status_ok = response.status_code in expected
                else:
                    status_ok = response.status_code == expected
                
                results[test_case['name']] = {
                    "status_code": response.status_code,
                    "expected_ok": status_ok,
                    "response_length": len(response.text)
                }
                
                if status_ok:
                    print(f"    ✅ Handled correctly (HTTP {response.status_code})")
                else:
                    print(f"    ⚠️  Unexpected status: HTTP {response.status_code}")
                    
            except Exception as e:
                results[test_case['name']] = {
                    "error": str(e),
                    "expected_ok": False
                }
                print(f"    ❌ Exception: {str(e)}")
        
        return results
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run complete integration test suite"""
        print("🚀 SignToMe Integration Test Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test categories
        self.test_results = {
            "api_endpoints": self.test_api_endpoints(),
            "frontend": self.test_frontend_connectivity(),
            "aws_services": self.test_aws_services(),
            "performance": self.test_performance_benchmarks(),
            "error_handling": self.test_error_handling(),
            "test_duration": 0,
            "issues_found": self.issues_found
        }
        
        self.test_results["test_duration"] = time.time() - start_time
        
        # Generate summary
        print("\n" + "=" * 60)
        print("🎯 Integration Test Summary")
        print("=" * 60)
        
        # API Status
        api_results = self.test_results["api_endpoints"]
        api_success_count = sum(1 for result in api_results.values() if result.get("success", False))
        print(f"API Endpoints: {api_success_count}/{len(api_results)} signs processed successfully")
        
        # Frontend Status
        frontend_ok = self.test_results["frontend"].get("accessible", False)
        print(f"Frontend: {'✅ ACCESSIBLE' if frontend_ok else '❌ NOT ACCESSIBLE'}")
        
        # Performance Status
        perf_grade = self.test_results["performance"]["performance_grade"]
        print(f"Performance: Grade {perf_grade} ({self.test_results['performance']['avg_latency']:.2f}s avg)")
        
        # Issues Summary
        print(f"\n📋 Issues Found: {len(self.issues_found)}")
        for i, issue in enumerate(self.issues_found, 1):
            print(f"  {i}. {issue}")
        
        # Overall Status
        overall_score = (
            (api_success_count / len(api_results)) * 0.4 +
            (1.0 if frontend_ok else 0.0) * 0.3 +
            (1.0 if perf_grade in ['A', 'B'] else 0.5) * 0.3
        )
        
        if overall_score >= 0.9:
            status = "🎉 EXCELLENT - Demo Ready!"
        elif overall_score >= 0.7:
            status = "✅ GOOD - Minor issues to address"
        elif overall_score >= 0.5:
            status = "⚠️  FAIR - Several issues need attention"
        else:
            status = "❌ POOR - Major issues require fixing"
        
        print(f"\n🏆 Overall Status: {status}")
        print(f"📊 Test Duration: {self.test_results['test_duration']:.1f} seconds")
        
        return self.test_results

def main():
    """Run integration tests"""
    tester = SignToMeIntegrationTest()
    results = tester.run_integration_tests()
    
    # Save results
    with open('/tmp/integration_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📁 Detailed results saved to: /tmp/integration_test_results.json")
    
    # Return exit code based on results
    return 0 if len(tester.issues_found) <= 2 else 1

if __name__ == "__main__":
    sys.exit(main())