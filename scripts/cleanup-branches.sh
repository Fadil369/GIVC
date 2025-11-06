#!/bin/bash

# Branch Cleanup Script - removes merged and stale branches

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🧹 Branch Cleanup Script"
echo "========================"
echo ""

cd /home/pi/GIVC

# Fetch latest
echo "Fetching latest from remote..."
git fetch --prune origin

echo ""
echo "Merged dependabot branches that can be deleted:"
git branch -r --merged main | grep 'dependabot' | sed 's|origin/||'

echo ""
echo "Other potentially stale branches:"
git branch -r | grep -E 'Q-DEV-issue|chore/test' | sed 's|origin/||'

echo ""
echo -e "${YELLOW}To delete these branches on GitHub, use:${NC}"
echo "git push origin --delete <branch-name>"
echo ""
echo "Or delete via GitHub web interface:"
echo "https://github.com/Fadil369/GIVC/branches"

