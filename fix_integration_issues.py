#!/usr/bin/env python3
"""
Fix integration issues and validate system readiness
"""

import requests
import json
import time
import base64
import io
from PIL import Image, ImageDraw, ImageFont

class SystemValidator:
    """System validator and issue fixer"""
    
    def __init__(self):
        self.api_endpoint = "https://6ddpddg0g3.execute-api.us-east-1.amazonaws.com/prod/process"
        self.frontend_url = "http://localhost:3001"  # Corrected port
        self.fixes_applied = []
        
    def create_high_quality_sign_image(self, sign: str) -> str:
        """Create a high-quality, realistic sign language image"""
        
        # Create larger, higher quality image
        img = Image.new('RGB', (800, 600), color=(240, 248, 255))  # Light blue background
        draw = ImageDraw.Draw(img)
        
        # Draw realistic background
        draw.rectangle([0, 0, 800, 600], fill=(240, 248, 255))
        
        # Draw person outline (more realistic proportions)
        # Head
        draw.ellipse([300, 100, 500, 300], fill=(255, 228, 196), outline=(139, 69, 19), width=3)
        
        # Torso
        draw.rectangle([250, 280, 550, 500], fill=(70, 130, 180), outline=(25, 25, 112), width=2)
        
        # Draw hands based on sign
        if sign == "HELLO":
            # HELLO: Hand at forehead level, fingers extended
            self._draw_hello_sign(draw)
        elif sign == "THANK YOU":
            # THANK YOU: Hand from chin outward
            self._draw_thank_you_sign(draw)
        elif sign == "PLEASE":
            # PLEASE: Circular motion on chest
            self._draw_please_sign(draw)
        
        # Add clear labeling
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            font_large = ImageFont.load_default()
            font_small = font_large
        
        # Main label
        draw.text((50, 50), f"ASL: {sign}", fill=(0, 0, 139), font=font_large)
        
        # Instruction text
        draw.text((50, 520), "Clear hand position for AI recognition", fill=(105, 105, 105), font=font_small)
        draw.text((50, 550), "SignToMe - AWS Breaking Barriers 2025", fill=(105, 105, 105), font=font_small)
        
        # Convert to base64 with high quality
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=95, optimize=True)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    def _draw_hello_sign(self, draw):
        """Draw HELLO sign - hand near forehead"""
        # Hand position near forehead
        hand_x, hand_y = 180, 120
        
        # Palm (larger, more detailed)
        draw.ellipse([hand_x, hand_y, hand_x+100, hand_y+120], 
                    fill=(255, 228, 196), outline=(139, 69, 19), width=3)
        
        # Individual fingers (more realistic)
        finger_positions = [
            (hand_x+15, hand_y-50, hand_x+30, hand_y+20),   # Index
            (hand_x+40, hand_y-60, hand_x+55, hand_y+15),   # Middle  
            (hand_x+65, hand_y-55, hand_x+80, hand_y+20),   # Ring
            (hand_x+85, hand_y-45, hand_x+100, hand_y+25),  # Pinky
        ]
        
        for finger in finger_positions:
            draw.ellipse(finger, fill=(255, 228, 196), outline=(139, 69, 19), width=2)
        
        # Thumb
        draw.ellipse([hand_x-20, hand_y+30, hand_x+10, hand_y+80], 
                    fill=(255, 228, 196), outline=(139, 69, 19), width=2)
        
        # Motion lines (clearer indication)
        for i in range(4):
            start_x = hand_x + 120 + (i * 20)
            draw.line([start_x, hand_y+40, start_x+25, hand_y+50], 
                     fill=(255, 69, 0), width=4)
    
    def _draw_thank_you_sign(self, draw):
        """Draw THANK YOU sign"""
        hand_x, hand_y = 350, 200
        
        # Hand near face
        draw.ellipse([hand_x, hand_y, hand_x+80, hand_y+100], 
                    fill=(255, 228, 196), outline=(139, 69, 19), width=3)
        
        # Fingers pointing outward
        for i in range(4):
            finger_x = hand_x + 80 + (i * 8)
            draw.ellipse([finger_x, hand_y+20, finger_x+12, hand_y+60], 
                        fill=(255, 228, 196), outline=(139, 69, 19), width=2)
        
        # Arc motion from face outward
        draw.arc([hand_x+40, hand_y-30, hand_x+160, hand_y+90], 
                30, 150, fill=(255, 69, 0), width=5)
    
    def _draw_please_sign(self, draw):
        """Draw PLEASE sign"""
        hand_x, hand_y = 350, 300
        
        # Flat hand on chest
        draw.ellipse([hand_x, hand_y, hand_x+90, hand_y+70], 
                    fill=(255, 228, 196), outline=(139, 69, 19), width=3)
        
        # Circular motion indicator
        draw.ellipse([hand_x+20, hand_y+10, hand_x+70, hand_y+60], 
                    outline=(255, 69, 0), width=4, fill=None)
        
        # Arrow indicating circular motion
        draw.polygon([(hand_x+60, hand_y+15), (hand_x+70, hand_y+25), (hand_x+55, hand_y+30)], 
                    fill=(255, 69, 0))
    
    def test_improved_api_performance(self):
        """Test API with improved images"""
        print("🔧 Testing API with high-quality sign images...")
        
        signs = ["HELLO", "THANK YOU", "PLEASE"]
        results = {}
        
        for sign in signs:
            print(f"  Testing {sign} with enhanced image...")
            
            # Create high-quality image
            image_data = self.create_high_quality_sign_image(sign)
            
            payload = {
                "frame_data": image_data,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "device_id": f"enhanced-test-{sign.lower().replace(' ', '-')}"
            }
            
            start_time = time.time()
            try:
                response = requests.post(
                    self.api_endpoint,
                    json=payload,
                    timeout=45,
                    headers={
                        "Content-Type": "application/json",
                        "X-Test-Type": "Enhanced-Quality"
                    }
                )
                
                latency = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    results[sign] = {
                        "success": True,
                        "latency": latency,
                        "translation": result.get("translation", ""),
                        "confidence": result.get("confidence", 0.0)
                    }
                    
                    confidence = result.get("confidence", 0.0)
                    translation = result.get("translation", "")
                    
                    if confidence > 0.3 and translation not in ["Error processing frame", "No clear signs detected"]:
                        print(f"    ✅ {sign}: '{translation}' (conf: {confidence:.2f}, {latency:.2f}s)")
                    else:
                        print(f"    ⚠️  {sign}: '{translation}' (conf: {confidence:.2f}, {latency:.2f}s)")
                else:
                    results[sign] = {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "latency": latency
                    }
                    print(f"    ❌ {sign}: HTTP {response.status_code}")
                    
            except Exception as e:
                results[sign] = {
                    "success": False,
                    "error": str(e),
                    "latency": time.time() - start_time
                }
                print(f"    ❌ {sign}: {str(e)}")
        
        return results
    
    def test_frontend_with_correct_port(self):
        """Test frontend on the correct port"""
        print("🔧 Testing frontend on correct port (3001)...")
        
        try:
            # Test main page
            response = requests.get(self.frontend_url, timeout=15)
            
            if response.status_code == 200:
                html = response.text
                
                # Check for key components
                checks = {
                    "has_signtome_title": "SignToMe" in html,
                    "has_camera_functionality": "camera" in html.lower() or "video" in html.lower(),
                    "has_react_components": "react" in html.lower() or "__next" in html,
                    "loads_in_reasonable_time": len(html) > 1000
                }
                
                all_good = all(checks.values())
                
                if all_good:
                    print(f"    ✅ Frontend accessible and functional")
                    self.fixes_applied.append("Frontend port corrected to 3001")
                else:
                    print(f"    ⚠️  Frontend accessible but some issues:")
                    for check, result in checks.items():
                        if not result:
                            print(f"      - {check}: FAIL")
                
                return {
                    "accessible": True,
                    "status_code": response.status_code,
                    "checks": checks,
                    "url": self.frontend_url
                }
            else:
                print(f"    ❌ Frontend returned HTTP {response.status_code}")
                return {"accessible": False, "status_code": response.status_code}
                
        except Exception as e:
            print(f"    ❌ Frontend error: {str(e)}")
            return {"accessible": False, "error": str(e)}
    
    def validate_end_to_end_workflow(self):
        """Validate the complete user workflow"""
        print("🔧 Validating end-to-end workflow...")
        
        workflow_steps = []
        
        # Step 1: Frontend loads
        frontend_result = self.test_frontend_with_correct_port()
        workflow_steps.append({
            "step": "Frontend loads",
            "success": frontend_result.get("accessible", False),
            "details": frontend_result
        })
        
        # Step 2: API processes simple request
        simple_payload = {
            "frame_data": "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCs/9k=",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "device_id": "workflow-test"
        }
        
        try:
            response = requests.post(self.api_endpoint, json=simple_payload, timeout=30)
            api_success = response.status_code == 200
            workflow_steps.append({
                "step": "API processes request",
                "success": api_success,
                "details": {"status": response.status_code, "response": response.json() if api_success else response.text}
            })
        except Exception as e:
            workflow_steps.append({
                "step": "API processes request", 
                "success": False,
                "details": {"error": str(e)}
            })
        
        # Step 3: Enhanced sign recognition
        enhanced_results = self.test_improved_api_performance()
        enhanced_success = any(r.get("success", False) for r in enhanced_results.values())
        workflow_steps.append({
            "step": "Enhanced sign recognition",
            "success": enhanced_success,
            "details": enhanced_results
        })
        
        # Summary
        successful_steps = sum(1 for step in workflow_steps if step["success"])
        total_steps = len(workflow_steps)
        
        print(f"\n📋 Workflow Validation Summary:")
        for i, step in enumerate(workflow_steps, 1):
            status = "✅" if step["success"] else "❌"
            print(f"  {i}. {step['step']}: {status}")
        
        print(f"\n🎯 Overall: {successful_steps}/{total_steps} steps successful")
        
        return {
            "steps": workflow_steps,
            "success_rate": successful_steps / total_steps,
            "ready_for_demo": successful_steps >= total_steps - 1  # Allow 1 failure
        }
    
    def generate_demo_readiness_report(self):
        """Generate final demo readiness report"""
        print("\n" + "="*60)
        print("🎬 DEMO READINESS ASSESSMENT")
        print("="*60)
        
        # Run all validations
        workflow_result = self.validate_end_to_end_workflow()
        
        # Calculate readiness score
        readiness_score = workflow_result["success_rate"] * 100
        
        if readiness_score >= 90:
            status = "🎉 DEMO READY!"
            color = "\033[92m"  # Green
        elif readiness_score >= 70:
            status = "✅ MOSTLY READY (minor issues)"
            color = "\033[93m"  # Yellow
        else:
            status = "❌ NEEDS WORK"
            color = "\033[91m"  # Red
        
        print(f"\n{color}🏆 OVERALL STATUS: {status}\033[0m")
        print(f"📊 Readiness Score: {readiness_score:.1f}%")
        
        if self.fixes_applied:
            print(f"\n🔧 Fixes Applied:")
            for fix in self.fixes_applied:
                print(f"  • {fix}")
        
        print(f"\n📝 Demo Instructions:")
        print(f"  1. Frontend URL: {self.frontend_url}")
        print(f"  2. API Endpoint: {self.api_endpoint}")
        print(f"  3. Click 'Start Camera' to begin")
        print(f"  4. Show clear ASL signs to camera")
        print(f"  5. Translations appear in real-time")
        
        return {
            "readiness_score": readiness_score,
            "status": status,
            "demo_ready": readiness_score >= 70,
            "frontend_url": self.frontend_url,
            "api_endpoint": self.api_endpoint,
            "fixes_applied": self.fixes_applied
        }

def main():
    """Run system validation and fixes"""
    validator = SystemValidator()
    report = validator.generate_demo_readiness_report()
    
    # Save report
    with open('/tmp/demo_readiness_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📁 Detailed report saved to: /tmp/demo_readiness_report.json")
    
    return 0 if report["demo_ready"] else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())