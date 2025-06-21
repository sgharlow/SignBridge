#!/bin/bash

# Fix App Runner Authentication Configuration Error
# This script creates the required IAM role for ECR access

set -e

echo "🔧 Fixing App Runner Authentication Configuration"
echo "=============================================="

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ROLE_NAME="AppRunnerECRAccessRole"
REGION="us-east-1"
SERVICE_NAME="signbridge-frontend"

echo "📋 AWS Account ID: $ACCOUNT_ID"

# Create IAM role trust policy
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
echo "🔐 Creating IAM role for App Runner ECR access..."
if ! aws iam get-role --role-name $ROLE_NAME >/dev/null 2>&1; then
    echo "✨ Creating new IAM role..."
    aws iam create-role --role-name $ROLE_NAME --assume-role-policy-document file://trust-policy.json
    aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess
    echo "⏳ Waiting for role to propagate..."
    sleep 15
    echo "✅ IAM role created successfully"
else
    echo "✅ IAM role already exists"
fi

ROLE_ARN="arn:aws:iam::$ACCOUNT_ID:role/$ROLE_NAME"

# Check if the service exists and delete it if it's in a failed state
echo "🔍 Checking existing App Runner service..."
if aws apprunner describe-service --service-arn "arn:aws:apprunner:$REGION:$ACCOUNT_ID:service/$SERVICE_NAME" >/dev/null 2>&1; then
    SERVICE_STATUS=$(aws apprunner describe-service --service-arn "arn:aws:apprunner:$REGION:$ACCOUNT_ID:service/$SERVICE_NAME" --query 'Service.Status' --output text)
    echo "🔍 Current service status: $SERVICE_STATUS"
    
    if [ "$SERVICE_STATUS" = "CREATE_FAILED" ] || [ "$SERVICE_STATUS" = "OPERATION_IN_PROGRESS" ]; then
        echo "🗑️  Deleting failed service..."
        aws apprunner delete-service --service-arn "arn:aws:apprunner:$REGION:$ACCOUNT_ID:service/$SERVICE_NAME"
        echo "⏳ Waiting for service deletion..."
        aws apprunner wait service-operation-successful --service-arn "arn:aws:apprunner:$REGION:$ACCOUNT_ID:service/$SERVICE_NAME" 2>/dev/null || true
        echo "✅ Failed service deleted"
    fi
fi

echo "✅ Authentication configuration fixed!"
echo ""
echo "🚀 Now run the deployment script again:"
echo "./deploy-apprunner.sh"
echo ""
echo "Or create the service manually with the IAM role:"
echo "Role ARN: $ROLE_ARN"

# Cleanup
rm -f trust-policy.json