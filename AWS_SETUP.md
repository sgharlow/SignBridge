# AWS Configuration for SignBridge Deployment

## Step 1: Configure AWS CLI

You need to configure your AWS CLI with credentials that have the following permissions:

### Required AWS Services Access:
- **ECR (Elastic Container Registry)** - For Docker image storage
- **App Runner** - For serverless container deployment  
- **Lambda** - Already configured for your backend
- **API Gateway** - Already configured for your backend
- **Bedrock** - Already configured for AI processing

### Configuration Command:
```bash
aws configure
```

You'll need to provide:
- **AWS Access Key ID**: Your access key
- **AWS Secret Access Key**: Your secret key  
- **Default region**: `us-east-1` (recommended)
- **Default output format**: `json` (recommended)

### Alternative: AWS SSO Configuration
If your organization uses AWS SSO:
```bash
aws configure sso
```

### Alternative: Environment Variables
```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=us-east-1
```

## Step 2: Verify Configuration

Test your AWS configuration:
```bash
aws sts get-caller-identity
```

This should return your AWS account information.

## Step 3: Check Required Permissions

Verify you have access to required services:
```bash
# Check ECR access
aws ecr describe-repositories --region us-east-1

# Check App Runner access  
aws apprunner list-services --region us-east-1

# Check existing API Gateway (should return your current API)
aws apigateway get-rest-apis --region us-east-1
```

## Step 4: Deploy SignBridge

Once AWS is configured, run the deployment:
```bash
./deploy-apprunner.sh
```

## IAM Policy Requirements

If you need to create an IAM user specifically for this deployment, attach these policies:

### Managed Policies:
- `AmazonEC2ContainerRegistryFullAccess`
- `AWSAppRunnerFullAccess`

### Custom Policy for Minimal Access:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:*",
                "apprunner:*",
                "iam:CreateServiceLinkedRole",
                "iam:PassRole"
            ],
            "Resource": "*"
        }
    ]
}
```

## Troubleshooting

**"Access Denied" errors:**
- Verify your AWS credentials are correct
- Check that your IAM user/role has the required permissions
- Ensure you're using the correct AWS region (us-east-1)

**"Service not found" errors:**
- App Runner may not be available in all regions
- Ensure you're using us-east-1 region
- Check AWS service health dashboard

**Docker errors:**
- Ensure Docker is installed and running
- On Windows, make sure Docker Desktop is started
- Check that you have sufficient disk space

## Troubleshooting Common Issues

### "Authentication configuration is invalid" Error

If you get this error during App Runner deployment:

```bash
# Run the fix script first
./fix-apprunner-auth.sh

# Then retry deployment
./deploy-apprunner.sh
```

This creates the required IAM role for App Runner to access ECR.

### IAM Permission Issues

If you get access denied errors, ensure your AWS credentials have these permissions:

- `ecr:*` - For container registry operations
- `apprunner:*` - For App Runner service management  
- `iam:CreateRole` - For creating service roles
- `iam:AttachRolePolicy` - For attaching policies to roles

### Service Creation Failures

1. **Check AWS region** - App Runner must be deployed in `us-east-1`
2. **Verify ECR image** - Ensure Docker image was pushed successfully
3. **IAM role propagation** - Wait 10-15 seconds after creating IAM roles

## Support

After configuring AWS CLI, the deployment script will:
1. ✅ Create required IAM roles automatically
2. ✅ Create ECR repository for your Docker images
3. ✅ Build and push your SignBridge frontend image  
4. ✅ Create App Runner service with proper configuration
5. ✅ Provide you with the live URL for your application

The entire process takes about 5-10 minutes.