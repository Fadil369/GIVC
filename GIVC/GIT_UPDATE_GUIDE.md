# Git Update Guide for GIVC Repository

## Quick Update

If you've already run the integration and want to push changes to your remote GIVC repository:

### Option 1: Using the Automated Script (Recommended)

```cmd
cd C:\Users\rcmrejection3\nphies-rcm\GIVC
git-update.bat
```

This will:
1. Check git status
2. Stage all changes
3. Create a comprehensive commit
4. Pull latest changes
5. Push to remote repository

### Option 2: Manual Git Commands

```cmd
cd C:\Users\rcmrejection3\nphies-rcm\GIVC

# Check what's changed
git status

# Add all changes
git add .

# Commit with message
git commit -m "Ultimate Integration: Merged NPHIES, AI, and monorepo features"

# Pull latest (if needed)
git pull origin main --rebase

# Push to remote
git push origin main
```

## Before Running Integration

If you haven't run the integration yet, you should:

1. **First, run the integration**:
   ```cmd
   cd C:\Users\rcmrejection3\nphies-rcm
   integrate.bat
   ```

2. **Then update the repository**:
   ```cmd
   cd GIVC
   git-update.bat
   ```

## What Will Be Committed

After running the integration, these new items will be added to GIVC:

### New Directories
- `backend/` - Enhanced Python backend with NPHIES integration
- `apps/` - Monorepo applications (from brainsait-rcm)
- `packages/` - Shared packages (from brainsait-rcm)
- `certificates/` - NPHIES production certificates
- `infrastructure/` - Kubernetes, Terraform configs
- `oasis-templates/` - OASIS HTML automation files
- `tests/nphies/` - NPHIES-specific tests

### New Files
- `ULTIMATE_INTEGRATION_GUIDE.md` - Complete platform documentation
- `backend/main_nphies.py` - FastAPI application
- `backend/requirements_nphies.txt` - Python dependencies
- `config/nphies-portals.yaml` - Portal configurations
- `.env.nphies.example` - Environment template
- `turbo_rcm.json` - Turbo configuration

### Enhanced Directories
- `docs/` - Added 10+ new documentation files
  - `NPHIES_INTEGRATION_GUIDE.md`
  - `AI_FEATURES_GUIDE.md`
  - `RCM_DEPLOYMENT_GUIDE.md`
  - And more...

## Git Best Practices

### Check Before Committing

```cmd
# See what's changed
git status

# See specific changes
git diff

# See changes in specific file
git diff ULTIMATE_INTEGRATION_GUIDE.md
```

### Selective Commits

If you want to commit only specific changes:

```cmd
# Add specific file
git add ULTIMATE_INTEGRATION_GUIDE.md

# Add specific directory
git add backend/

# Commit
git commit -m "Add NPHIES integration documentation"
```

### Handling Sensitive Files

Make sure `.gitignore` excludes:
- `.env` (actual environment variables)
- `certificates/*.pem` (actual certificates - keep private!)
- `node_modules/`
- `venv/` or `.venv/`
- `__pycache__/`

Check your `.gitignore`:
```cmd
type .gitignore
```

## Troubleshooting

### Authentication Issues

If you get authentication errors:

1. **Use GitHub Personal Access Token**:
   ```cmd
   git config credential.helper store
   git push origin main
   # Enter username and token (not password)
   ```

2. **Or configure SSH**:
   ```cmd
   git remote set-url origin git@github.com:YOUR_USERNAME/GIVC.git
   ```

### Conflicts

If you get merge conflicts:

```cmd
# See conflicted files
git status

# Edit files to resolve conflicts
# Look for <<<<<<< markers

# After resolving
git add .
git commit -m "Resolved merge conflicts"
git push origin main
```

### Large Files

If you have large files (>100MB):

```cmd
# Install Git LFS
git lfs install

# Track large files
git lfs track "*.pem"
git lfs track "certificates/*"

# Commit .gitattributes
git add .gitattributes
git commit -m "Configure Git LFS"
```

## Verification

After pushing, verify your changes:

1. Visit your GitHub repository
2. Check the commits tab
3. Verify all files are present
4. Check the README displays correctly

## Branch Strategy (Optional)

For production deployments, consider using branches:

```cmd
# Create integration branch
git checkout -b integration/nphies-ai-merge

# Commit changes
git add .
git commit -m "Integration changes"

# Push to branch
git push origin integration/nphies-ai-merge

# Create Pull Request on GitHub
# Review and merge to main
```

## Commit Message Template

For detailed commits:

```
Title: Brief description (50 chars)

Body:
- What was changed
- Why it was changed
- How to test

Features Added:
- Feature 1
- Feature 2

Breaking Changes:
- None or list them

References:
- Issue #123
- PR #456
```

## Remote Repository Info

Check your remote configuration:

```cmd
# View remote URL
git remote -v

# Change remote URL if needed
git remote set-url origin https://github.com/YOUR_USERNAME/GIVC.git

# Add additional remote
git remote add upstream https://github.com/ORIGINAL_OWNER/GIVC.git
```

## Summary

**Quick Update Process**:
1. Run `integrate.bat` (if not done yet)
2. Review changes with `git status`
3. Run `git-update.bat` to push all changes
4. Verify on GitHub

**Important**: Make sure to exclude sensitive files (actual `.env`, certificates) from commits!

---

**Created**: January 2024  
**For**: GIVC Ultimate Integration  
**Version**: 3.0.0
