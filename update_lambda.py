#!/usr/bin/env python3
"""
Quick script to update Lambda function code directly
"""

import boto3
import zipfile
import os
import tempfile

def update_lambda_function():
    # Lambda function name
    function_name = "SignToMeStack-SignProcessorFunctionB88A65F7-Kln8aYzk9Q5T"
    
    # Read the handler.py file
    handler_path = "/mnt/c/Users/sghar/CascadeProjects/signtome/backend/lambda/handler.py"
    requirements_path = "/mnt/c/Users/sghar/CascadeProjects/signtome/backend/lambda/requirements.txt"
    
    # Create a temporary zip file
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
        with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add handler.py
            zip_file.write(handler_path, 'handler.py')
            # Add requirements.txt
            zip_file.write(requirements_path, 'requirements.txt')
        
        temp_zip_path = temp_zip.name
    
    try:
        # Update Lambda function
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        with open(temp_zip_path, 'rb') as zip_data:
            response = lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_data.read()
            )
        
        print("✅ Lambda function updated successfully!")
        print(f"Function: {response['FunctionName']}")
        print(f"Version: {response['Version']}")
        print(f"Last Modified: {response['LastModified']}")
        
    except Exception as e:
        print(f"❌ Error updating Lambda function: {e}")
    
    finally:
        # Clean up temp file
        os.unlink(temp_zip_path)

if __name__ == "__main__":
    update_lambda_function()