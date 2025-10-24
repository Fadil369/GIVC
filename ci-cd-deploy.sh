#!/bin/bash

# GIVC Platform - CI/CD Deployment Script
# Purpose: Automated deployment from git

set -e

DEPLOY_LOG="ci-cd-deploy-$(date +%Y%m%d-%H%M%S).log"

echo "Starting CI/CD deployment..." | tee -a "$DEPLOY_LOG"

# Pull latest changes
echo "Pulling latest code..." | tee -a "$DEPLOY_LOG"
git pull origin main 2>&1 | tee -a "$DEPLOY_LOG"

# Run tests
echo "Running tests..." | tee -a "$DEPLOY_LOG"
./test-deployment.sh 2>&1 | tee -a "$DEPLOY_LOG"

# Build and deploy
echo "Building containers..." | tee -a "$DEPLOY_LOG"
docker-compose build --no-cache 2>&1 | tee -a "$DEPLOY_LOG"

echo "Deploying services..." | tee -a "$DEPLOY_LOG"
docker-compose up -d 2>&1 | tee -a "$DEPLOY_LOG"

# Wait for services
echo "Waiting for services..." | tee -a "$DEPLOY_LOG"
sleep 10

# Verify deployment
echo "Verifying deployment..." | tee -a "$DEPLOY_LOG"
./test-deployment.sh 2>&1 | tee -a "$DEPLOY_LOG"

echo "✅ Deployment complete!" | tee -a "$DEPLOY_LOG"
