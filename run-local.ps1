# PowerShell script to run Blog CMS locally on Windows
# This script helps set up and run the application without Docker

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Blog CMS - Local Setup for Windows" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.12 from https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host ""
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Check PostgreSQL
Write-Host ""
Write-Host "Checking PostgreSQL..." -ForegroundColor Yellow
$pgService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
if ($pgService) {
    Write-Host "✓ PostgreSQL service found" -ForegroundColor Green
} else {
    Write-Host "⚠ PostgreSQL not detected. Please install from https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
    Write-Host "  After installation, create database:" -ForegroundColor Yellow
    Write-Host "  CREATE DATABASE blogdb;" -ForegroundColor Gray
    Write-Host "  CREATE USER bloguser WITH PASSWORD 'blogpass';" -ForegroundColor Gray
    Write-Host "  GRANT ALL PRIVILEGES ON DATABASE blogdb TO bloguser;" -ForegroundColor Gray
}

# Check Redis
Write-Host ""
Write-Host "Checking Redis..." -ForegroundColor Yellow
$redisProcess = Get-Process -Name "redis-server" -ErrorAction SilentlyContinue
if ($redisProcess) {
    Write-Host "✓ Redis is running" -ForegroundColor Green
} else {
    Write-Host "⚠ Redis not running. Download from https://github.com/microsoftarchive/redis/releases" -ForegroundColor Yellow
    Write-Host "  Extract and run redis-server.exe" -ForegroundColor Yellow
}

# Check if database is initialized
Write-Host ""
Write-Host "Checking database..." -ForegroundColor Yellow
if (-not (Test-Path "migrations")) {
    Write-Host "Initializing database migrations..." -ForegroundColor Yellow
    $env:FLASK_APP = "wsgi.py"
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
    Write-Host "✓ Database initialized" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "Seeding database with sample data..." -ForegroundColor Yellow
    flask seed-db
    Write-Host "✓ Database seeded" -ForegroundColor Green
} else {
    Write-Host "✓ Database already initialized" -ForegroundColor Green
}

# Display instructions
Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To run the application, open 3 separate PowerShell windows:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Window 1 - Flask App:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "  `$env:FLASK_APP='wsgi.py'" -ForegroundColor Gray
Write-Host "  flask run --host=0.0.0.0 --port=5000" -ForegroundColor Gray
Write-Host ""
Write-Host "Window 2 - Celery Worker:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "  celery -A app.extensions.celery worker --loglevel=info --pool=solo" -ForegroundColor Gray
Write-Host ""
Write-Host "Window 3 - Celery Beat:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "  celery -A app.extensions.celery beat --loglevel=info" -ForegroundColor Gray
Write-Host ""
Write-Host "Access the application at:" -ForegroundColor Yellow
Write-Host "  Blog: http://localhost:5000" -ForegroundColor Green
Write-Host "  Admin: http://localhost:5000/admin" -ForegroundColor Green
Write-Host "  API Docs: http://localhost:5000/api/v1/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Default Admin Login:" -ForegroundColor Yellow
Write-Host "  Email: admin@blog.com" -ForegroundColor Green
Write-Host "  Password: admin123" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to start Flask now, or Ctrl+C to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Start Flask
Write-Host ""
Write-Host "Starting Flask application..." -ForegroundColor Green
$env:FLASK_APP = "wsgi.py"
flask run --host=0.0.0.0 --port=5000