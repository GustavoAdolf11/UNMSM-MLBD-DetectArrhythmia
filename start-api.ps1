# PowerShell script to start the API
# Usage: .\start-api.ps1

Write-Host "================================" -ForegroundColor Cyan
Write-Host "ECG Arrhythmia Detection API" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "[INFO] Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
Write-Host "[INFO] Activating virtual environment..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

# Install/update dependencies
Write-Host "[INFO] Checking dependencies..." -ForegroundColor Cyan
pip install -q --upgrade pip

if (-not (pip show fastapi 2>$null)) {
    Write-Host "[INFO] Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements-api.txt
} else {
    Write-Host "[OK] Dependencies already installed" -ForegroundColor Green
}

# Check .env file
if (-not (Test-Path ".env")) {
    Write-Host "[INFO] Creating .env from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
}

# Check model files
if (-not (Test-Path "models\ecg_nv_cnn\model_v7.keras")) {
    Write-Host "[WARNING] Model file not found!" -ForegroundColor Red
    Write-Host "  Please run: python deteccionarritmias.py" -ForegroundColor Yellow
    Write-Host "  Or copy model files to: models\ecg_nv_cnn\" -ForegroundColor Yellow
    Write-Host ""
}

# Run validation tests
Write-Host ""
Write-Host "[INFO] Running validation tests..." -ForegroundColor Cyan
python test_api.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] Validation failed. Please fix errors above." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "Starting API Server..." -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "📍 URL: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🏥 Health: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the API
python main.py
