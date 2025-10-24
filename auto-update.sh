#!/bin/bash

# GIVC Platform - Auto Update
# Purpose: Automated updates with rollback capability

set -e

BACKUP_DIR="backups/pre-update-$(date +%Y%m%d-%H%M%S)"

echo "Creating pre-update backup..."
mkdir -p "$BACKUP_DIR"

# Backup current state
docker-compose ps > "$BACKUP_DIR/containers.txt"
cp docker-compose.yml "$BACKUP_DIR/"
cp .env "$BACKUP_DIR/"

# Create database backup
./backup.sh

# Pull updates
git fetch origin
git stash
git pull origin main

# Update dependencies
if [ -f requirements.txt ]; then
    docker-compose build backend
fi

# Deploy updates
docker-compose up -d

# Test
sleep 10
if ./test-deployment.sh; then
    echo "✅ Update successful!"
    echo "Backup location: $BACKUP_DIR"
else
    echo "❌ Update failed! Rolling back..."
    cp "$BACKUP_DIR/docker-compose.yml" .
    docker-compose up -d
    exit 1
fi
