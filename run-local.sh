#!/bin/bash

# SignBridge Local Development Server
# AWS Breaking Barriers Hackathon 2025

echo "🌉 SignBridge - Local Development Server"
echo "========================================"

# Navigate to frontend directory
cd frontend

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "⚙️  Creating local environment config..."
    cp .env.example .env.local
fi

echo "🚀 Starting SignBridge locally..."
echo "📱 Open http://localhost:3000 in your browser"
echo "🔗 Backend API: Configure your API Gateway endpoint in .env.local"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the development server
npm run dev