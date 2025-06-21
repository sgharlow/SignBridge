# SignBridge Deployment Guide

## AWS App Runner Deployment

### Prerequisites
- AWS CLI v2+ configured with appropriate permissions
- Docker installed and running
- AWS account with Bedrock access enabled

### Quick Deployment

1. **Clone and Build**
   ```bash
   git clone <repository-url>
   cd signtome
   ```

2. **Deploy to App Runner**
   ```bash
   ./deploy-apprunner.sh
   ```

3. **Access Your App**
   The script will output your live URL when deployment completes.

### Manual Deployment Steps

1. **Build Frontend**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Create ECR Repository**
   ```bash
   aws ecr create-repository --repository-name signbridge-frontend --region us-east-1
   ```

3. **Build and Push Docker Image**
   ```bash
   # Get your account ID
   ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
   
   # Build and tag
   docker build -t signbridge-frontend .
   docker tag signbridge-frontend:latest $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/signbridge-frontend:latest
   
   # Login and push
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
   docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/signbridge-frontend:latest
   ```

4. **Create App Runner Service**
   ```bash
   aws apprunner create-service --cli-input-json file://frontend/apprunner-config.json
   ```

### Environment Variables

The following environment variables are configured automatically:

- `NODE_ENV=production`
- `NEXT_PUBLIC_API_ENDPOINT=https://6ddpddg0g3.execute-api.us-east-1.amazonaws.com/prod/process`

### Monitoring

After deployment, monitor your service:

1. **App Runner Console**
   - Navigate to AWS App Runner in the console
   - View service metrics and logs

2. **Health Check**
   ```bash
   curl -I https://your-app-runner-url.amazonaws.com
   ```

### Troubleshooting

**Build Failures:**
- Check that all dependencies are properly installed
- Verify Docker is running
- Ensure AWS credentials are configured

**Service Not Starting:**
- Check App Runner service logs in AWS console
- Verify environment variables are set correctly
- Ensure ECR image was pushed successfully

**API Connection Issues:**
- Verify Lambda function is deployed and accessible
- Check CORS configuration in API Gateway
- Test API endpoint directly

### Cost Optimization

App Runner pricing is based on:
- vCPU and memory allocation (0.25 vCPU, 0.5 GB)
- Active time only (scales to zero when not in use)
- Data transfer

Estimated cost: ~$5-10/month for demo usage

### Security Considerations

- All traffic is encrypted with HTTPS
- No sensitive data is stored in environment variables
- API Gateway provides rate limiting
- Lambda functions use least-privilege IAM roles

## Local Development

For local development instead of App Runner:

```bash
cd frontend
npm install
npm run dev
```

Access at http://localhost:3000

## Support

For deployment issues:
- Check AWS CloudTrail for API errors
- Review App Runner service logs
- Verify IAM permissions for ECR and App Runner