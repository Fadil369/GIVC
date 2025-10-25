#!/bin/bash

# GIVC Multi-Platform Deployment Script
# This script deploys the enhanced GIVC platform to multiple Cloudflare Pages projects

set -e

echo "🚀 GIVC Multi-Platform Deployment Script"
echo "========================================="

# Build the application first
echo "🔨 Building application..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed. Exiting..."
    exit 1
fi

echo "✅ Build completed successfully!"

# Function to deploy to a specific project
deploy_to_project() {
    local project_name=$1
    local description=$2
    
    echo ""
    echo "🌎 Deploying to: $project_name"
    echo "   Description: $description"
    echo "   URL: https://$project_name.pages.dev"
    
    wrangler pages deploy dist --project-name="$project_name" --commit-dirty=true
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully deployed to $project_name"
    else
        echo "❌ Failed to deploy to $project_name"
        return 1
    fi
}

# Check command line arguments
if [ $# -eq 0 ]; then
    echo ""
    echo "📋 Available deployment options:"
    echo "  ./deploy.sh all           - Deploy to all projects"
    echo "  ./deploy.sh main          - Deploy to givc (main platform)"
    echo "  ./deploy.sh static        - Deploy to givc-platform-static"
    echo "  ./deploy.sh ui            - Deploy to givc-healthcare-ui"
    echo "  ./deploy.sh platform      - Deploy to givc-healthcare-platform"
    echo "  ./deploy.sh healthcare    - Deploy to givc-healthcare"
    echo ""
    echo "💡 Recommended: Start with 'static' for clean deployment"
    exit 0
fi

case $1 in
    "all")
        echo "🎯 Deploying to all GIVC projects..."
        deploy_to_project "givc" "Main enhanced platform"
        deploy_to_project "givc-platform-static" "Clean enhanced deployment"
        deploy_to_project "givc-healthcare-ui" "UI-focused deployment"
        deploy_to_project "givc-healthcare-platform" "Platform-focused deployment"
        deploy_to_project "givc-healthcare" "Healthcare-focused deployment"
        ;;
    "main")
        deploy_to_project "givc" "Main enhanced platform"
        ;;
    "static")
        deploy_to_project "givc-platform-static" "Clean enhanced deployment (Recommended)"
        ;;
    "ui")
        deploy_to_project "givc-healthcare-ui" "UI-focused deployment"
        ;;
    "platform")
        deploy_to_project "givc-healthcare-platform" "Platform-focused deployment"
        ;;
    "healthcare")
        deploy_to_project "givc-healthcare" "Healthcare-focused deployment"
        ;;
    *)
        echo "❌ Unknown option: $1"
        echo "💡 Run './deploy.sh' without arguments to see available options"
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment completed!"
echo ""
echo "📋 Deployment Summary:"
echo "======================"
echo "✅ Main Platform:        https://givc.pages.dev"
echo "✅ Static Platform:      https://givc-platform-static.pages.dev"
echo "💼 Healthcare UI:        https://givc-healthcare-ui.pages.dev"
echo "🏥 Healthcare Platform:  https://givc-healthcare-platform.pages.dev"
echo "🩺 Healthcare System:    https://givc-healthcare.pages.dev"
echo ""
echo "🌟 All platforms now feature:"
echo "   • Professional UI with loading skeletons"
echo "   • Toast notification system"
echo "   • Enhanced mobile responsiveness"
echo "   • AI-powered healthcare features"
echo "   • Insurance management system"
echo "   • Medical agents and triage"
echo ""
echo "🚀 Integration complete! Choose your preferred platform URL."
