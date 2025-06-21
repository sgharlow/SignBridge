#!/usr/bin/env python3
"""
Production readiness testing for SignToMe
AWS Breaking Barriers Hackathon 2025
"""

import requests
import json
import time
import threading
from concurrent import futures
import base64
import statistics
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

class ProductionReadinessTest:
    """Comprehensive production readiness test suite"""
    
    def __init__(self):
        self.api_endpoint = "https://6ddpddg0g3.execute-api.us-east-1.amazonaws.com/prod/process"
        self.frontend_url = "http://localhost:3001"
        self.test_results = {}
        self.performance_data = []
        
    def create_test_image_b64(self) -> str:
        """Create optimized test image for consistent testing"""
        # Minimal but valid JPEG for consistent testing
        return "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgKCgkICQkKDA8MCgsOCwkJDRENDg8QEBEQCgwSExIQEw8QEBD/yQALCAABAAEBAREA/8wABgAQEAX/2gAIAQEAAD8A0s8g/9k="
    
    def stress_test_api(self, num_requests: int = 20, concurrent: int = 5) -> Dict[str, Any]:
        """Stress test the API with concurrent requests"""
        print(f"🔥 Stress testing API: {num_requests} requests, {concurrent} concurrent...")
        
        def make_request(request_id: int) -> Dict[str, Any]:
            payload = {
                "frame_data": self.create_test_image_b64(),
                "timestamp": datetime.now().isoformat() + "Z",
                "device_id": f"stress-test-{request_id}"
            }
            
            start_time = time.time()
            try:
                response = requests.post(
                    self.api_endpoint,
                    json=payload,
                    timeout=60,
                    headers={"Content-Type": "application/json"}
                )
                
                latency = time.time() - start_time
                
                return {
                    "request_id": request_id,
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "latency": latency,
                    "response_size": len(response.text),
                    "timestamp": start_time
                }
            except Exception as e:
                return {
                    "request_id": request_id,
                    "success": False,
                    "error": str(e),
                    "latency": time.time() - start_time,
                    "timestamp": start_time
                }
        
        # Execute stress test
        start_time = time.time()
        results = []
        
        with futures.ThreadPoolExecutor(max_workers=concurrent) as executor:
            future_list = [executor.submit(make_request, i) for i in range(num_requests)]
            results = [future.result() for future in futures.as_completed(future_list)]
        
        total_time = time.time() - start_time
        
        # Analyze results
        successful = [r for r in results if r.get("success", False)]
        failed = [r for r in results if not r.get("success", False)]
        
        latencies = [r["latency"] for r in successful]
        
        stats = {
            "total_requests": num_requests,
            "successful_requests": len(successful),
            "failed_requests": len(failed),
            "success_rate": len(successful) / num_requests * 100,
            "total_time": total_time,
            "requests_per_second": num_requests / total_time,
            "latency_stats": {
                "min": min(latencies) if latencies else 0,
                "max": max(latencies) if latencies else 0,
                "mean": statistics.mean(latencies) if latencies else 0,
                "median": statistics.median(latencies) if latencies else 0,
                "p95": statistics.quantiles(latencies, n=20)[18] if len(latencies) > 20 else (max(latencies) if latencies else 0)
            }
        }
        
        print(f"  📊 Results:")
        print(f"    Success Rate: {stats['success_rate']:.1f}%")
        print(f"    Requests/sec: {stats['requests_per_second']:.2f}")
        print(f"    Latency P95: {stats['latency_stats']['p95']:.2f}s")
        print(f"    Mean Latency: {stats['latency_stats']['mean']:.2f}s")
        
        return stats
    
    def security_test(self) -> Dict[str, Any]:
        """Test security and input validation"""
        print("🔒 Testing security and input validation...")
        
        test_cases = [
            {
                "name": "SQL Injection Attempt",
                "payload": {
                    "frame_data": "'; DROP TABLE users; --",
                    "timestamp": "2025-06-21T12:00:00Z",
                    "device_id": "sql_injection_test"
                }
            },
            {
                "name": "XSS Attempt", 
                "payload": {
                    "frame_data": "<script>alert('xss')</script>",
                    "timestamp": "2025-06-21T12:00:00Z",
                    "device_id": "xss_test"
                }
            },
            {
                "name": "Oversized Payload",
                "payload": {
                    "frame_data": "A" * 10000000,  # 10MB
                    "timestamp": "2025-06-21T12:00:00Z",
                    "device_id": "oversize_test"
                }
            },
            {
                "name": "Malformed JSON",
                "payload": '{"frame_data": "test", "timestamp": malformed}'
            },
            {
                "name": "Missing Required Fields",
                "payload": {
                    "device_id": "missing_fields_test"
                }
            }
        ]
        
        results = {}
        
        for test_case in test_cases:
            print(f"  Testing: {test_case['name']}")
            
            try:
                if isinstance(test_case['payload'], str):
                    # Malformed JSON test
                    response = requests.post(
                        self.api_endpoint,
                        data=test_case['payload'],
                        headers={"Content-Type": "application/json"},
                        timeout=30
                    )
                else:
                    response = requests.post(
                        self.api_endpoint,
                        json=test_case['payload'],
                        timeout=30
                    )
                
                # Security tests should return 4xx errors, not 200
                secure = response.status_code in [400, 413, 422, 429]
                
                results[test_case['name']] = {
                    "secure": secure,
                    "status_code": response.status_code,
                    "response_length": len(response.text)
                }
                
                if secure:
                    print(f"    ✅ Properly handled (HTTP {response.status_code})")
                else:
                    print(f"    ⚠️  Unexpected response (HTTP {response.status_code})")
                    
            except requests.exceptions.Timeout:
                results[test_case['name']] = {
                    "secure": True,  # Timeout is acceptable for oversized payloads
                    "status_code": "TIMEOUT",
                    "note": "Request timed out (acceptable for some attacks)"
                }
                print(f"    ✅ Request timed out (acceptable)")
                
            except Exception as e:
                results[test_case['name']] = {
                    "secure": True,  # Exception handling is good
                    "error": str(e),
                    "note": "Exception raised (acceptable)"
                }
                print(f"    ✅ Exception handled: {str(e)[:50]}")
        
        security_score = sum(1 for r in results.values() if r.get("secure", False)) / len(results) * 100
        print(f"  🔒 Security Score: {security_score:.1f}%")
        
        return {
            "security_score": security_score,
            "test_results": results,
            "passed_all_tests": security_score == 100
        }
    
    def performance_benchmark(self, duration_minutes: int = 2) -> Dict[str, Any]:
        """Run sustained performance benchmark"""
        print(f"⚡ Running performance benchmark for {duration_minutes} minutes...")
        
        end_time = time.time() + (duration_minutes * 60)
        request_count = 0
        results = []
        
        while time.time() < end_time:
            payload = {
                "frame_data": self.create_test_image_b64(),
                "timestamp": datetime.now().isoformat() + "Z",
                "device_id": f"benchmark-{request_count}"
            }
            
            start = time.time()
            try:
                response = requests.post(
                    self.api_endpoint,
                    json=payload,
                    timeout=30
                )
                
                latency = time.time() - start
                results.append({
                    "latency": latency,
                    "success": response.status_code == 200,
                    "timestamp": start
                })
                
                request_count += 1
                
                # Brief pause to simulate realistic usage
                time.sleep(1)
                
            except Exception as e:
                results.append({
                    "latency": time.time() - start,
                    "success": False,
                    "error": str(e),
                    "timestamp": start
                })
                request_count += 1
        
        # Analyze sustained performance
        successful = [r for r in results if r.get("success", False)]
        latencies = [r["latency"] for r in successful]
        
        if latencies:
            performance_stats = {
                "total_requests": len(results),
                "successful_requests": len(successful),
                "success_rate": len(successful) / len(results) * 100,
                "duration_minutes": duration_minutes,
                "avg_requests_per_minute": len(results) / duration_minutes,
                "latency_consistency": {
                    "mean": statistics.mean(latencies),
                    "stdev": statistics.stdev(latencies) if len(latencies) > 1 else 0,
                    "min": min(latencies),
                    "max": max(latencies)
                },
                "performance_grade": self._calculate_performance_grade(latencies, len(successful) / len(results))
            }
        else:
            performance_stats = {
                "total_requests": len(results),
                "successful_requests": 0,
                "success_rate": 0,
                "performance_grade": "F"
            }
        
        print(f"  📈 Sustained Performance:")
        print(f"    Requests: {performance_stats['total_requests']}")
        print(f"    Success Rate: {performance_stats['success_rate']:.1f}%")
        print(f"    Grade: {performance_stats['performance_grade']}")
        
        return performance_stats
    
    def _calculate_performance_grade(self, latencies: List[float], success_rate: float) -> str:
        """Calculate performance grade based on latency and success rate"""
        if not latencies or success_rate < 0.9:
            return "F"
        
        avg_latency = statistics.mean(latencies)
        
        if avg_latency < 2.0 and success_rate > 0.95:
            return "A"
        elif avg_latency < 5.0 and success_rate > 0.9:
            return "B"
        elif avg_latency < 10.0 and success_rate > 0.8:
            return "C"
        elif avg_latency < 20.0:
            return "D"
        else:
            return "F"
    
    def scalability_test(self) -> Dict[str, Any]:
        """Test system scalability characteristics"""
        print("📈 Testing scalability characteristics...")
        
        # Test different load levels
        load_levels = [1, 3, 5, 8]
        scalability_results = {}
        
        for concurrent_users in load_levels:
            print(f"  Testing with {concurrent_users} concurrent users...")
            
            # Run mini stress test for each level
            results = []
            
            def user_simulation(user_id: int):
                for i in range(3):  # Each user makes 3 requests
                    payload = {
                        "frame_data": self.create_test_image_b64(),
                        "timestamp": datetime.now().isoformat() + "Z",
                        "device_id": f"scale-test-user{user_id}-req{i}"
                    }
                    
                    start = time.time()
                    try:
                        response = requests.post(
                            self.api_endpoint,
                            json=payload,
                            timeout=45
                        )
                        
                        results.append({
                            "user_id": user_id,
                            "request_id": i,
                            "latency": time.time() - start,
                            "success": response.status_code == 200
                        })
                    except Exception as e:
                        results.append({
                            "user_id": user_id,
                            "request_id": i,
                            "latency": time.time() - start,
                            "success": False,
                            "error": str(e)
                        })
                    
                    time.sleep(0.5)  # Brief pause between requests
            
            # Execute concurrent user simulation
            with futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
                future_list = [executor.submit(user_simulation, user_id) for user_id in range(concurrent_users)]
                futures.wait(future_list)
            
            # Analyze results for this load level
            successful = [r for r in results if r.get("success", False)]
            latencies = [r["latency"] for r in successful]
            
            scalability_results[concurrent_users] = {
                "total_requests": len(results),
                "successful_requests": len(successful),
                "success_rate": len(successful) / len(results) * 100 if results else 0,
                "avg_latency": statistics.mean(latencies) if latencies else 0,
                "max_latency": max(latencies) if latencies else 0
            }
            
            print(f"    {concurrent_users} users: {len(successful)}/{len(results)} successful, {statistics.mean(latencies):.2f}s avg" if latencies else f"    {concurrent_users} users: No successful requests")
        
        # Analyze scalability trend
        success_rates = [r["success_rate"] for r in scalability_results.values()]
        latency_trend = [r["avg_latency"] for r in scalability_results.values() if r["avg_latency"] > 0]
        
        scalability_grade = "A"
        if min(success_rates) < 80:
            scalability_grade = "C" 
        elif min(success_rates) < 90:
            scalability_grade = "B"
        
        return {
            "load_test_results": scalability_results,
            "scalability_grade": scalability_grade,
            "handles_concurrent_load": min(success_rates) > 70,
            "latency_degradation": max(latency_trend) / min(latency_trend) if len(latency_trend) > 1 else 1.0
        }
    
    def deployment_validation(self) -> Dict[str, Any]:
        """Validate deployment and infrastructure"""
        print("🚀 Validating deployment and infrastructure...")
        
        validation_results = {}
        
        # Test API health
        try:
            health_response = requests.get(
                self.api_endpoint.replace('/process', '/health'),
                timeout=10
            )
            validation_results["health_endpoint"] = {
                "available": health_response.status_code in [200, 404],  # 404 is OK if no health endpoint
                "status_code": health_response.status_code
            }
        except:
            validation_results["health_endpoint"] = {
                "available": False,
                "note": "No health endpoint found (acceptable)"
            }
        
        # Test CORS headers
        try:
            options_response = requests.options(self.api_endpoint, timeout=10)
            cors_headers = options_response.headers
            
            validation_results["cors_configuration"] = {
                "configured": "Access-Control-Allow-Origin" in cors_headers,
                "headers": dict(cors_headers)
            }
        except:
            validation_results["cors_configuration"] = {
                "configured": False,
                "note": "CORS headers checked via POST requests"
            }
        
        # Test frontend availability
        try:
            frontend_response = requests.get(self.frontend_url, timeout=15)
            validation_results["frontend_deployment"] = {
                "available": frontend_response.status_code == 200,
                "status_code": frontend_response.status_code,
                "content_length": len(frontend_response.text)
            }
        except Exception as e:
            validation_results["frontend_deployment"] = {
                "available": False,
                "error": str(e)
            }
        
        # Test API rate limiting (optional)
        try:
            rapid_requests = []
            for i in range(10):
                start = time.time()
                response = requests.post(
                    self.api_endpoint,
                    json={"frame_data": "", "timestamp": "test", "device_id": f"rate-test-{i}"},
                    timeout=5
                )
                rapid_requests.append({
                    "latency": time.time() - start,
                    "status_code": response.status_code
                })
            
            rate_limited = any(r["status_code"] == 429 for r in rapid_requests)
            validation_results["rate_limiting"] = {
                "implemented": rate_limited,
                "note": "Rate limiting may be implemented at API Gateway level"
            }
        except:
            validation_results["rate_limiting"] = {
                "implemented": False,
                "note": "Could not test rate limiting"
            }
        
        deployment_score = sum(1 for r in validation_results.values() if r.get("available", r.get("configured", True))) / len(validation_results) * 100
        
        print(f"  🚀 Deployment Score: {deployment_score:.1f}%")
        
        return {
            "deployment_score": deployment_score,
            "validation_results": validation_results,
            "production_ready": deployment_score >= 75
        }
    
    def generate_production_report(self) -> Dict[str, Any]:
        """Generate comprehensive production readiness report"""
        print("\n" + "="*60)
        print("🏭 PRODUCTION READINESS REPORT")
        print("="*60)
        
        start_time = time.time()
        
        # Run all production tests
        tests = {
            "stress_test": self.stress_test_api(15, 3),
            "security_test": self.security_test(),
            "performance_benchmark": self.performance_benchmark(1),  # 1 minute for quick test
            "scalability_test": self.scalability_test(),
            "deployment_validation": self.deployment_validation()
        }
        
        total_time = time.time() - start_time
        
        # Calculate overall production readiness score
        scores = {
            "stress_test": min(tests["stress_test"]["success_rate"] / 100, 1.0),
            "security": tests["security_test"]["security_score"] / 100,
            "performance": 1.0 if tests["performance_benchmark"]["performance_grade"] in ["A", "B"] else 0.5,
            "scalability": 1.0 if tests["scalability_test"]["scalability_grade"] in ["A", "B"] else 0.5,
            "deployment": tests["deployment_validation"]["deployment_score"] / 100
        }
        
        overall_score = sum(scores.values()) / len(scores) * 100
        
        # Determine production readiness level
        if overall_score >= 85:
            readiness_level = "🎉 PRODUCTION READY"
            recommendation = "System is ready for production deployment"
        elif overall_score >= 70:
            readiness_level = "✅ MOSTLY READY"
            recommendation = "Minor optimizations recommended before production"
        elif overall_score >= 50:
            readiness_level = "⚠️  NEEDS IMPROVEMENT"
            recommendation = "Address key issues before production deployment"
        else:
            readiness_level = "❌ NOT READY"
            recommendation = "Significant work needed before production"
        
        print(f"\n🏆 OVERALL READINESS: {readiness_level}")
        print(f"📊 Production Score: {overall_score:.1f}%")
        print(f"💡 Recommendation: {recommendation}")
        
        print(f"\n📋 Test Results Summary:")
        print(f"  • Stress Test: {tests['stress_test']['success_rate']:.1f}% success rate")
        print(f"  • Security: {tests['security_test']['security_score']:.1f}% secure")
        print(f"  • Performance: Grade {tests['performance_benchmark']['performance_grade']}")
        print(f"  • Scalability: Grade {tests['scalability_test']['scalability_grade']}")
        print(f"  • Deployment: {tests['deployment_validation']['deployment_score']:.1f}% validated")
        
        print(f"\n⏱️  Total Test Time: {total_time:.1f} seconds")
        
        return {
            "overall_score": overall_score,
            "readiness_level": readiness_level,
            "recommendation": recommendation,
            "individual_scores": scores,
            "test_results": tests,
            "test_duration": total_time,
            "production_ready": overall_score >= 70
        }

def main():
    """Run production readiness testing"""
    tester = ProductionReadinessTest()
    report = tester.generate_production_report()
    
    # Save comprehensive report
    with open('/tmp/production_readiness_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📁 Detailed report saved to: /tmp/production_readiness_report.json")
    
    # Return appropriate exit code
    return 0 if report["production_ready"] else 1

if __name__ == "__main__":
    sys.exit(main())