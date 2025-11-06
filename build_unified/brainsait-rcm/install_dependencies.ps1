# NPM Dependency Installation Script
# Handles network timeouts and provides fallback options

$ErrorActionPreference = "Continue"
$base = "C:\Users\rcmrejection3\nphies-rcm\GIVC\build_unified\brainsait-rcm"
Set-Location $base

Write-Output "==================================================================="
Write-Output "  NPM DEPENDENCY INSTALLATION & VULNERABILITY FIX"
Write-Output "==================================================================="
Write-Output ""

# Step 1: Check npm and node versions
Write-Output "Step 1: Checking environment..."
try {
    $npmVer = npm --version
    $nodeVer = node --version
    Write-Output "  ✓ npm version: $npmVer"
    Write-Output "  ✓ node version: $nodeVer"
} catch {
    Write-Output "  ✗ ERROR: npm or node not found in PATH"
    Write-Output "  Please install Node.js from https://nodejs.org/"
    exit 1
}
Write-Output ""

# Step 2: Clean previous installation attempts
Write-Output "Step 2: Cleaning previous installation..."
if (Test-Path "node_modules") {
    Write-Output "  Removing node_modules..."
    Remove-Item node_modules -Recurse -Force -ErrorAction SilentlyContinue
}
if (Test-Path "package-lock.json") {
    Write-Output "  Removing package-lock.json..."
    Remove-Item package-lock.json -Force -ErrorAction SilentlyContinue
}
Write-Output "  ✓ Cleaned"
Write-Output ""

# Step 3: Configure npm for better reliability
Write-Output "Step 3: Configuring npm..."
npm config set fetch-timeout 120000
npm config set fetch-retry-mintimeout 30000
npm config set fetch-retry-maxtimeout 180000
npm config set registry https://registry.npmjs.org/
Write-Output "  ✓ Configured"
Write-Output ""

# Step 4: Install dependencies
Write-Output "Step 4: Installing dependencies..."
Write-Output "  This may take 5-10 minutes depending on network speed..."
Write-Output ""

$installSuccess = $false
$attempts = 0
$maxAttempts = 3

while (-not $installSuccess -and $attempts -lt $maxAttempts) {
    $attempts++
    Write-Output "  Attempt $attempts of $maxAttempts..."
    
    # Try install
    $installOutput = npm install --legacy-peer-deps 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        $installSuccess = $true
        Write-Output "  ✓ Dependencies installed successfully!"
    } else {
        Write-Output "  ⚠ Install failed (exit code: $LASTEXITCODE)"
        if ($attempts -lt $maxAttempts) {
            Write-Output "  Retrying in 5 seconds..."
            Start-Sleep -Seconds 5
        }
    }
}

if (-not $installSuccess) {
    Write-Output ""
    Write-Output "  ✗ Installation failed after $maxAttempts attempts"
    Write-Output ""
    Write-Output "MANUAL FALLBACK OPTIONS:"
    Write-Output "  1. Check your internet connection"
    Write-Output "  2. Try using a different npm registry:"
    Write-Output "     npm config set registry https://registry.npmmirror.com/"
    Write-Output "  3. Install offline using a cached registry"
    Write-Output "  4. Install critical packages individually:"
    Write-Output "     npm install turbo@latest --save-dev"
    Write-Output "     npm install typescript@latest --save-dev"
    Write-Output ""
    exit 1
}

Write-Output ""

# Step 5: Verify installation
Write-Output "Step 5: Verifying installation..."
if (Test-Path "node_modules") {
    $pkgCount = (Get-ChildItem node_modules -Directory).Count
    Write-Output "  ✓ node_modules created with $pkgCount packages"
} else {
    Write-Output "  ✗ node_modules not found!"
    exit 1
}
Write-Output ""

# Step 6: Upgrade Hono to fix vulnerability
Write-Output "Step 6: Upgrading Hono package (security fix)..."
$honoUpgrade = npm update hono --legacy-peer-deps 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Output "  ✓ Hono upgraded successfully"
} else {
    Write-Output "  ⚠ Hono upgrade had issues (may not be a direct dependency)"
}
Write-Output ""

# Step 7: Run security audit
Write-Output "Step 7: Running security audit..."
$auditOutput = npm audit --json 2>&1 | ConvertFrom-Json -ErrorAction SilentlyContinue
if ($auditOutput) {
    $vulns = $auditOutput.metadata.vulnerabilities
    Write-Output "  Vulnerabilities found:"
    Write-Output "    Critical: $($vulns.critical)"
    Write-Output "    High:     $($vulns.high)"
    Write-Output "    Moderate: $($vulns.moderate)"
    Write-Output "    Low:      $($vulns.low)"
} else {
    Write-Output "  (Audit data unavailable)"
}
Write-Output ""

# Step 8: Test build capability
Write-Output "Step 8: Testing build capability..."
if (Test-Path "node_modules/.bin/turbo") {
    Write-Output "  ✓ Turbo installed correctly"
    Write-Output "  Ready to run: npm run build"
} else {
    Write-Output "  ⚠ Turbo not found in expected location"
}
Write-Output ""

Write-Output "==================================================================="
Write-Output "  INSTALLATION COMPLETE"
Write-Output "==================================================================="
Write-Output ""
Write-Output "NEXT STEPS:"
Write-Output "  1. Run builds:  npm run build"
Write-Output "  2. Run tests:   npm run test"
Write-Output "  3. Run dev:     npm run dev"
Write-Output ""
Write-Output "SECURITY:"
Write-Output "  - Review audit results above"
Write-Output "  - Apply fixes: npm audit fix --force"
Write-Output "  - Update deps: npm update"
Write-Output ""
