# Script para iniciar MLflow UI en Windows
# Uso: .\start_mlflow.ps1

# Activar entorno virtual si existe
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "Activando entorno virtual..." -ForegroundColor Yellow
    .\venv\Scripts\Activate.ps1
}

Write-Host "Iniciando MLflow UI..." -ForegroundColor Green
Write-Host ""

# Verificar que mlflow esta instalado
try {
    $version = python -c "import mlflow; print(mlflow.__version__)" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "MLflow $version detectado" -ForegroundColor Green
    } else {
        throw "MLflow no encontrado"
    }
} catch {
    Write-Host "MLflow no esta instalado" -ForegroundColor Red
    Write-Host "   Instalando MLflow..." -ForegroundColor Yellow
    pip install mlflow
}

Write-Host ""
Write-Host "Iniciando servidor MLflow..." -ForegroundColor Cyan
Write-Host "   URL: http://127.0.0.1:5000" -ForegroundColor Yellow
Write-Host "   Presiona Ctrl+C para detener" -ForegroundColor Gray
Write-Host ""

# Iniciar MLflow UI
python -m mlflow ui --host 127.0.0.1 --port 5000
