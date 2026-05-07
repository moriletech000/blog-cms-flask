# Check prerequisites for running Blog CMS

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Blog CMS - Prerequisites Check" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# Check Python
Write-Host "1. Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "3\.1[2-9]") {
        Write-Host "   ✓ $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "   ✗ Python 3.12+ required. Found: $pythonVersion" -ForegroundColor Red
        Write-Host "   Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
        $allGood = $false
    }
} catch {
    Write-Host "   ✗ Python not found" -ForegroundColor Red
    Write-Host "   Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    $allGood = $false
}

# Check Docker (optional)
Write-Host ""
Write-Host "2. Checking Docker (optional)..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "   ✓ $dockerVersion" -ForegroundColor Green
    Write-Host "   You can use Docker to run the application!" -ForegroundColor Cyan
} catch {
    Write-Host "   ⚠ Docker not found (optional)" -ForegroundColor Yellow
    Write-Host "   For easier setup, install Docker Desktop:" -ForegroundColor Yellow
    Write-Host "   https://www.docker.com/products/docker-desktop/" -ForegroundColor Gray
}

# Check PostgreSQL
Write-Host ""
Write-Host "3. Checking PostgreSQL..." -ForegroundColor Yellow
$pgService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
if ($pgService) {
    Write-Host "   ✓ PostgreSQL service found: $($pgService.DisplayName)" -ForegroundColor Green
} else {
    Write-Host "   ✗ PostgreSQL not found" -ForegroundColor Red
    Write-Host "   Download from: https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
    $allGood = $false
}

# Check Redis
Write-Host ""
Write-Host "4. Checking Redis..." -ForegroundColor Yellow
$redisProcess = Get-Process -Name "redis-server" -ErrorAction SilentlyContinue
if ($redisProcess) {
    Write-Host "   ✓ Redis is running" -ForegroundColor Green
} else {
    Write-Host "   ✗ Redis not running" -ForegroundColor Red
    Write-Host "   Download from: https://github.com/microsoftarchive/redis/releases" -ForegroundColor Yellow
    $allGood = $false
}

# Check Git
Write-Host ""
Write-Host "5. Checking Git..." -ForegroundColor Yellow
try {
    $gitVersion = git --version 2>&1
    Write-Host "   ✓ $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "   ⚠ Git not found (optional)" -ForegroundColor Yellow
    Write-Host "   Download from: https://git-scm.com/download/win" -ForegroundColor Gray
}

# Summary
Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

if ($allGood) {
    Write-Host "✓ All required prerequisites are installed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Run: .\run-local.ps1" -ForegroundColor Cyan
    Write-Host "   This will set up and start the application" -ForegroundColor Gray
} else {
    Write-Host "✗ Some prerequisites are missing" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install the missing components above, then run this script again." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternative: Install Docker Desktop for easier setup" -ForegroundColor Cyan
    Write-Host "https://www.docker.com/products/docker-desktop/" -ForegroundColor Gray
}

Write-Host ""
Write-Host "For detailed setup instructions, see:" -ForegroundColor Yellow
Write-Host "  - WINDOWS_SETUP.md (just created)" -ForegroundColor Cyan
Write-Host "  - QUICKSTART.md" -ForegroundColor Cyan
Write-Host "  - README.md" -ForegroundColor Cyan
Write-Host ""