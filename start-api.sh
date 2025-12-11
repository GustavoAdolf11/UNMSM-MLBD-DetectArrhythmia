#!/bin/bash
# Bash script to start the API (Linux/Mac)
# Usage: ./start-api.sh

set -e

echo "================================"
echo "ECG Arrhythmia Detection API"
echo "================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[INFO] Virtual environment not found. Creating..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "[INFO] Checking dependencies..."
pip install -q --upgrade pip

if ! pip show fastapi > /dev/null 2>&1; then
    echo "[INFO] Installing dependencies..."
    pip install -r requirements-api.txt
else
    echo "[OK] Dependencies already installed"
fi

# Check .env file
if [ ! -f ".env" ]; then
    echo "[INFO] Creating .env from template..."
    cp .env.example .env
fi

# Check model files
if [ ! -f "models/ecg_nv_cnn/model_v7.keras" ]; then
    echo "[WARNING] Model file not found!"
    echo "  Please run: python deteccionarritmias.py"
    echo "  Or copy model files to: models/ecg_nv_cnn/"
    echo ""
fi

# Run validation tests
echo ""
echo "[INFO] Running validation tests..."
python test_api.py

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Validation failed. Please fix errors above."
    exit 1
fi

echo ""
echo "================================"
echo "Starting API Server..."
echo "================================"
echo ""
echo "📍 URL: http://localhost:8000"
echo "📚 Docs: http://localhost:8000/docs"
echo "🏥 Health: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the API
python main.py
