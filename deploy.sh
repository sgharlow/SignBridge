#!/bin/bash

# SignToMe Deployment Script
# AWS Breaking Barriers Hackathon 2025

set -e

echo "🚀 Starting SignToMe deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v node &> /dev/null; then
    print_error "Node.js not found. Please install Node.js 18+"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    print_error "npm not found. Please install npm"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    print_error "AWS CLI not found. Please install AWS CLI"
    exit 1
fi

print_status "Prerequisites check passed"

# Set AWS environment
export AWS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Deploy backend infrastructure
echo ""
echo "📡 Deploying backend infrastructure..."
cd infrastructure
if npm run deploy; then
    print_status "Backend infrastructure deployed"
else
    print_error "Backend deployment failed"
    exit 1
fi
cd ..

# Build and prepare frontend
echo ""
echo "🎨 Building frontend..."
cd frontend
if npm run build; then
    print_status "Frontend build completed"
else
    print_error "Frontend build failed"
    exit 1
fi
cd ..

# Test API endpoint
echo ""
echo "🧪 Testing API endpoint..."
API_ENDPOINT=$(aws cloudformation describe-stacks --stack-name SignToMeStack --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' --output text)

if [ -n "$API_ENDPOINT" ]; then
    print_status "API endpoint found: $API_ENDPOINT"
    
    # Test with a simple ping
    if curl -s -X POST "$API_ENDPOINT" -H "Content-Type: application/json" -d '{}' > /dev/null; then
        print_status "API endpoint is responsive"
    else
        print_warning "API endpoint test failed (may be normal for empty payload)"
    fi
else
    print_error "Could not retrieve API endpoint"
    exit 1
fi

# Display deployment summary
echo ""
echo "🎉 Deployment Summary"
echo "====================="
echo "Backend API: $API_ENDPOINT"
echo "Frontend: Available for local testing with 'npm run dev'"
echo ""
echo "📋 Next Steps:"
echo "1. Start frontend: cd frontend && npm run dev"
echo "2. Open browser to: http://localhost:3000"
echo "3. Allow camera access when prompted"
echo "4. Test sign language interpretation"
echo ""
echo "🏆 Ready for AWS Breaking Barriers Hackathon demo!"

print_status "Deployment completed successfully!"