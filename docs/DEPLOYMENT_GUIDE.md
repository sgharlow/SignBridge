# SignToMe - Deployment Guide

**AWS Breaking Barriers Hackathon 2025**

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Infrastructure Deployment](#infrastructure-deployment)
4. [Application Deployment](#application-deployment)
5. [Configuration](#configuration)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)
8. [Production Considerations](#production-considerations)

---

## Prerequisites

### Required Software

| Tool | Version | Purpose |
|------|---------|---------|
| AWS CLI | 2.x+ | AWS service management |
| Node.js | 18.x+ | Frontend and CDK |
| npm | 8.x+ | Package management |
| Python | 3.9+ | Lambda functions |
| Git | 2.x+ | Source code management |

### AWS Account Requirements

**Required Services Access**:
- ✅ Amazon Bedrock (with Claude 3.5 Sonnet access)
- ✅ AWS Lambda
- ✅ Amazon API Gateway
- ✅ AWS IoT Core
- ✅ Amazon S3
- ✅ AWS CloudFormation
- ✅ AWS IAM

**Estimated Costs**:
- **Development**: $0-10/month (within free tier limits)
- **Demo Usage**: $10-50/month (moderate usage)
- **Production**: $100-500/month (depends on scale)

### Required Permissions

**IAM Policy Requirements**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "lambda:*",
        "apigateway:*",
        "iot:*",
        "s3:*",
        "cloudformation:*",
        "iam:*",
        "logs:*"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## Environment Setup

### 1. AWS CLI Configuration

```bash
# Install AWS CLI (if not already installed)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure
# AWS Access Key ID: [Enter your access key]
# AWS Secret Access Key: [Enter your secret key]
# Default region name: us-east-1
# Default output format: json

# Verify configuration
aws sts get-caller-identity
```

### 2. Enable AWS Bedrock Access

**Important**: Bedrock model access must be enabled in your AWS account.

```bash
# Check available models
aws bedrock list-foundation-models --region us-east-1

# If Claude models not available, request access via AWS Console:
# 1. Go to AWS Bedrock Console
# 2. Navigate to "Model access"
# 3. Request access to Anthropic Claude models
# 4. Wait for approval (usually immediate for most accounts)
```

### 3. Node.js and CDK Setup

```bash
# Install Node.js (if not already installed)
# Download from https://nodejs.org/ or use package manager

# Install AWS CDK globally
npm install -g aws-cdk

# Verify installation
cdk --version
node --version
npm --version
```

### 4. SSL Certificate Setup (Linux/WSL)

```bash
# Set SSL certificate bundle for AWS CLI
export AWS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Add to shell profile for persistence
echo 'export AWS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt' >> ~/.bashrc
source ~/.bashrc
```

---

## Infrastructure Deployment

### 1. Clone and Setup Repository

```bash
# Clone the repository
git clone <repository-url>
cd signtome

# Install dependencies
npm install

# Verify project structure
ls -la
# Should see: frontend/, backend/, infrastructure/, docs/
```

### 2. CDK Bootstrap

**First-time setup only**:
```bash
# Bootstrap CDK in your AWS account/region
cdk bootstrap

# Expected output:
# ✅ Environment aws://ACCOUNT-ID/us-east-1 bootstrapped
```

### 3. Deploy Infrastructure

```bash
# Deploy the complete infrastructure stack
npx cdk deploy --require-approval never

# Monitor deployment progress
# This will create:
# - Lambda functions
# - API Gateway
# - IoT Core resources
# - S3 buckets
# - IAM roles and policies
```

**Expected Output**:
```
✅  SignToMeStack

✨  Deployment time: 120.45s

Outputs:
SignToMeStack.ApiEndpoint = https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/
SignToMeStack.DataBucket = signtome-data-461293170793
SignToMeStack.LambdaFunction = SignToMeStack-SignProcessorFunction-XXXXX
```

### 4. Verify Infrastructure

```bash
# Check CloudFormation stack
aws cloudformation describe-stacks --stack-name SignToMeStack

# Test API endpoint
curl -X POST [API_ENDPOINT]/process \
  -H "Content-Type: application/json" \
  -d '{"frame_data": "", "timestamp": "2025-06-21T12:00:00Z", "device_id": "test"}'

# Expected: {"error": "No frame data provided"} (400 status)
```

---

## Application Deployment

### 1. Frontend Deployment

```bash
# Navigate to frontend directory
cd frontend

# Install frontend dependencies
npm install

# Build for production
npm run build

# Start development server
npm run dev

# Expected output:
# ✓ Ready in 2.5s
# - Local: http://localhost:3000 (or 3001 if 3000 is busy)
```

### 2. Environment Configuration

Create frontend environment file:
```bash
# Create .env.local in frontend directory
cd frontend
cat > .env.local << EOF
NEXT_PUBLIC_API_ENDPOINT=https://[YOUR-API-ID].execute-api.us-east-1.amazonaws.com/prod/process
EOF
```

### 3. Backend Verification

```bash
# Check Lambda function
aws lambda get-function --function-name [LAMBDA_FUNCTION_NAME]

# Check recent logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/SignToMeStack"

# Test with sample data
python3 backend/test_api.py
```

---

## Configuration

### 1. Infrastructure Configuration

**CDK Stack Parameters** (`infrastructure/cdk-stack.ts`):
```typescript
// Customize these values as needed
const config = {
  lambdaTimeout: 30, // seconds
  lambdaMemory: 128, // MB
  apiThrottling: {
    rateLimit: 100,  // requests per second
    burstLimit: 200  // burst capacity
  }
};
```

### 2. Lambda Configuration

**Environment Variables** (automatically set by CDK):
```bash
BEDROCK_REGION=us-east-1
DATA_BUCKET=signtome-data-[account-id]
```

### 3. Frontend Configuration

**API Endpoint Configuration** (`frontend/.env.local`):
```bash
NEXT_PUBLIC_API_ENDPOINT=https://[api-id].execute-api.us-east-1.amazonaws.com/prod/process
```

### 4. Performance Tuning

**Lambda Memory Optimization**:
```bash
# Test different memory settings
aws lambda update-function-configuration \
  --function-name [FUNCTION_NAME] \
  --memory-size 256

# Monitor performance impact
aws logs filter-log-events \
  --log-group-name /aws/lambda/[FUNCTION_NAME] \
  --filter-pattern "REPORT"
```

---

## Testing

### 1. Integration Testing

```bash
# Run comprehensive integration tests
python3 test_integration.py

# Expected output:
# 🎯 Integration Test Summary
# API Endpoints: 3/3 signs processed successfully
# Frontend: ✅ ACCESSIBLE
# Overall Status: ✅ DEMO READY
```

### 2. Production Readiness Testing

```bash
# Run production readiness tests
python3 production_readiness_test.py

# Expected output:
# 🏆 OVERALL READINESS: ✅ MOSTLY READY
# 📊 Production Score: 83.0%
```

### 3. Performance Testing

```bash
# Run load testing
python3 test_realtime_pipeline.py

# Monitor results:
# - Success Rate: 100%
# - Average Latency: <3 seconds
# - Concurrent Users: 5+ supported
```

### 4. Manual Testing

**Frontend Testing**:
1. Open http://localhost:3001
2. Click "Start Camera"
3. Allow camera permissions
4. Perform ASL signs
5. Verify real-time translations

**API Testing**:
```bash
# Test with curl
curl -X POST [API_ENDPOINT] \
  -H "Content-Type: application/json" \
  -d '{
    "frame_data": "/9j/4AAQSkZJRgABAQEAYABgAAD/...",
    "timestamp": "2025-06-21T12:00:00Z",
    "device_id": "manual-test"
  }'
```

---

## Troubleshooting

### Common Issues

#### 1. CDK Bootstrap Fails

**Problem**: `The security token included in the request is invalid`

**Solution**:
```bash
# Refresh AWS credentials
aws configure
aws sts get-caller-identity

# Re-run bootstrap
cdk bootstrap
```

#### 2. Lambda Timeout Errors

**Problem**: API returns 504 Gateway Timeout

**Solutions**:
```bash
# Increase Lambda timeout
aws lambda update-function-configuration \
  --function-name [FUNCTION_NAME] \
  --timeout 60

# Check CloudWatch logs
aws logs tail /aws/lambda/[FUNCTION_NAME] --follow
```

#### 3. Bedrock Access Denied

**Problem**: `AccessDeniedException` when calling Bedrock

**Solutions**:
1. Enable Bedrock model access in AWS Console
2. Check IAM permissions for Bedrock
3. Verify region supports Claude models

```bash
# Check Bedrock access
aws bedrock list-foundation-models --region us-east-1
```

#### 4. Frontend Build Errors

**Problem**: TypeScript compilation errors

**Solution**:
```bash
cd frontend

# Clear cache and reinstall
rm -rf node_modules .next
npm install

# Fix specific errors
npm run build
```

#### 5. CORS Issues

**Problem**: Browser blocks API requests

**Verify CORS headers**:
```bash
curl -X OPTIONS [API_ENDPOINT] -v
# Should include Access-Control-Allow-Origin headers
```

### Debugging Commands

```bash
# Check CloudFormation stack status
aws cloudformation describe-stacks --stack-name SignToMeStack

# View Lambda function logs
aws logs tail /aws/lambda/[FUNCTION_NAME] --follow

# Check API Gateway logs
aws logs describe-log-groups --log-group-name-prefix "API-Gateway"

# Test Bedrock connectivity
aws bedrock list-foundation-models --region us-east-1

# Check S3 bucket
aws s3 ls s3://[BUCKET_NAME]
```

### Log Analysis

**Lambda Logs Location**:
```
/aws/lambda/SignToMeStack-SignProcessorFunction-[ID]
```

**Common Log Patterns**:
```bash
# Successful processing
grep "Processing completed" [log-file]

# Error patterns
grep "ERROR" [log-file]

# Performance metrics
grep "REPORT RequestId" [log-file]
```

---

## Production Considerations

### 1. Security Hardening

**API Security**:
```typescript
// Add API key requirement
const api = new apigateway.RestApi(this, 'SignToMeApi', {
  apiKeySourceType: apigateway.ApiKeySourceType.HEADER,
  // ... other config
});

// Create API key
const apiKey = new apigateway.ApiKey(this, 'ApiKey');
```

**IAM Least Privilege**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude*"
    }
  ]
}
```

### 2. Monitoring and Alerts

**CloudWatch Alarms**:
```bash
# Create error rate alarm
aws cloudwatch put-metric-alarm \
  --alarm-name "SignToMe-HighErrorRate" \
  --alarm-description "High error rate in SignToMe API" \
  --metric-name ErrorCount \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold
```

### 3. Cost Optimization

**Lambda Cost Optimization**:
- Use ARM-based Graviton2 processors
- Optimize memory allocation
- Implement request caching

**Bedrock Cost Management**:
```python
# Implement request optimization
def optimize_bedrock_request(frame_data):
    # Reduce image size for cost efficiency
    if len(frame_data) > 100000:  # 100KB
        frame_data = compress_image(frame_data, quality=70)
    
    return frame_data
```

### 4. Scalability Planning

**Auto Scaling Configuration**:
```typescript
// Lambda concurrent execution limit
const functionProps = {
  reservedConcurrentExecutions: 100,
  // ... other props
};
```

**Multi-Region Deployment**:
```bash
# Deploy to multiple regions
cdk deploy --context region=us-west-2
cdk deploy --context region=eu-west-1
```

### 5. Backup and Recovery

**S3 Cross-Region Replication**:
```typescript
const bucket = new s3.Bucket(this, 'DataBucket', {
  replicationConfiguration: {
    role: replicationRole.roleArn,
    rules: [{
      id: 'backup-rule',
      status: 'Enabled',
      destination: {
        bucket: backupBucket.bucketArn,
        storageClass: 'GLACIER'
      }
    }]
  }
});
```

### 6. Compliance Considerations

**GDPR Compliance**:
- Implement data retention policies
- Add user consent management
- Ensure data portability

**HIPAA Compliance** (for healthcare use):
- Enable AWS CloudTrail
- Implement encryption at rest
- Add audit logging

---

## Quick Reference

### Essential Commands

```bash
# Deploy infrastructure
npx cdk deploy --require-approval never

# Build and start frontend
cd frontend && npm run build && npm run dev

# Run tests
python3 test_integration.py

# Check API health
curl -X POST [API_ENDPOINT] -H "Content-Type: application/json" -d '{}'

# View logs
aws logs tail /aws/lambda/[FUNCTION_NAME] --follow

# Update Lambda code
npx cdk deploy SignToMeStack

# Cleanup resources
npx cdk destroy
```

### URLs and Endpoints

| Resource | URL/Endpoint |
|----------|--------------|
| Frontend | http://localhost:3001 |
| API Gateway | https://[api-id].execute-api.us-east-1.amazonaws.com/prod |
| AWS Console | https://console.aws.amazon.com |
| CloudFormation | https://console.aws.amazon.com/cloudformation |

### Support Resources

- **Documentation**: [Technical Specification](./TECHNICAL_SPECIFICATION.md)
- **API Reference**: [API Reference](./API_REFERENCE.md)
- **Demo Setup**: [Demo Setup Guide](../DEMO_SETUP.md)

---

**🚀 Deployment completed successfully for AWS Breaking Barriers Hackathon 2025!**