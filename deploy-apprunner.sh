#!/bin/bash

# SignBridge AWS App Runner Deployment Script
# AWS Breaking Barriers Hackathon 2025

set -e

echo "🌉 SignBridge - AWS App Runner Deployment"
echo "========================================"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

echo "✅ AWS CLI configured"

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "📋 AWS Account ID: $ACCOUNT_ID"

# Set variables
SERVICE_NAME="signbridge-frontend"
REGION="us-east-1"
ECR_REPOSITORY="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$SERVICE_NAME"
ROLE_NAME="AppRunnerECRAccessRole"

echo "🏗️  Building and deploying SignBridge frontend..."

# Create IAM role for App Runner ECR access
echo "🔐 Creating IAM role for App Runner..."
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "build.apprunner.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role if it doesn't exist
if ! aws iam get-role --role-name $ROLE_NAME >/dev/null 2>&1; then
    echo "✨ Creating new IAM role..."
    aws iam create-role --role-name $ROLE_NAME --assume-role-policy-document file://trust-policy.json
    aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess
    echo "⏳ Waiting for role to propagate..."
    sleep 10
else
    echo "✅ IAM role already exists"
fi

ROLE_ARN="arn:aws:iam::$ACCOUNT_ID:role/$ROLE_NAME"

# Navigate to frontend directory
cd frontend

# Create ECR repository if it doesn't exist
echo "📦 Creating ECR repository..."
aws ecr create-repository --repository-name $SERVICE_NAME --region $REGION 2>/dev/null || echo "ECR repository already exists"

# Get ECR login
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_REPOSITORY

# Build Docker image
echo "🐳 Building Docker image..."
docker build -t $SERVICE_NAME .

# Tag and push to ECR
echo "📤 Pushing to ECR..."
docker tag $SERVICE_NAME:latest $ECR_REPOSITORY:latest
docker push $ECR_REPOSITORY:latest

# Create App Runner service configuration
cat > apprunner-service.json << EOF
{
  "ServiceName": "$SERVICE_NAME",
  "SourceConfiguration": {
    "ImageRepository": {
      "ImageIdentifier": "$ECR_REPOSITORY:latest",
      "ImageConfiguration": {
        "Port": "3000",
        "RuntimeEnvironmentVariables": {
          "NODE_ENV": "production",
          "NEXT_PUBLIC_API_ENDPOINT": "https://your-api-gateway-endpoint.amazonaws.com/prod/process"
        }
      },
      "ImageRepositoryType": "ECR"
    },
    "AuthenticationConfiguration": {
      "AccessRoleArn": "$ROLE_ARN"
    },
    "AutoDeploymentsEnabled": false
  },
  "InstanceConfiguration": {
    "Cpu": "0.25 vCPU",
    "Memory": "0.5 GB"
  },
  "Tags": [
    {
      "Key": "Project",
      "Value": "SignBridge"
    },
    {
      "Key": "Environment",
      "Value": "Production"
    },
    {
      "Key": "Hackathon",
      "Value": "AWS-Breaking-Barriers-2025"
    }
  ]
}
EOF

# Create or update App Runner service
echo "🚀 Creating App Runner service..."
if aws apprunner describe-service --service-arn "arn:aws:apprunner:$REGION:$ACCOUNT_ID:service/$SERVICE_NAME" >/dev/null 2>&1; then
    echo "🔄 Service exists, updating..."
    aws apprunner update-service --service-arn "arn:aws:apprunner:$REGION:$ACCOUNT_ID:service/$SERVICE_NAME" --source-configuration file://apprunner-service.json
else
    echo "✨ Creating new service..."
    aws apprunner create-service --cli-input-json file://apprunner-service.json
fi

# Wait for service to be running
echo "⏳ Waiting for service to be ready..."
aws apprunner wait service-operation-successful --service-arn "arn:aws:apprunner:$REGION:$ACCOUNT_ID:service/$SERVICE_NAME"

# Get service URL
SERVICE_URL=$(aws apprunner describe-service --service-arn "arn:aws:apprunner:$REGION:$ACCOUNT_ID:service/$SERVICE_NAME" --query 'Service.ServiceUrl' --output text)

# Cleanup temporary files
rm -f trust-policy.json apprunner-service.json

echo "🎉 Deployment complete!"
echo "📱 Service URL: https://$SERVICE_URL"
echo "🔗 API Endpoint: https://6ddpddg0g3.execute-api.us-east-1.amazonaws.com/prod/process"
echo ""
echo "🧪 Test your deployment:"
echo "curl -I https://$SERVICE_URL"
echo ""
echo "🌉 SignBridge is now live on AWS App Runner!"