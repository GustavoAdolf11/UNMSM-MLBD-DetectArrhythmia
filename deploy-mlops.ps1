# ============================================================================
# Script de Despliegue a Hugging Face con IntegraciÃ³n MLOps
# ============================================================================
# Este script:
# 1. Busca el mejor modelo en MLflow (por F1-Score de clase V)
# 2. Lo copia al directorio de producciÃ³n
# 3. Prepara archivos para Hugging Face
# 4. Despliega automÃ¡ticamente
#
# Uso: .\deploy-to-hf-mlops.ps1
# ============================================================================

Write-Host ""
Write-Host "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—" -ForegroundColor Cyan
Write-Host "â•‘   ðŸš€ Despliegue a Hugging Face con MLOps                   â•‘" -ForegroundColor Cyan
Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host ""

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "deteccionarritmias.py")) {
    Write-Host "âŒ Error: Ejecuta este script desde el directorio raÃ­z del proyecto" -ForegroundColor Red
    exit 1
}

# ============================================================================
# PASO 1: Buscar mejor modelo en MLflow
# ============================================================================
Write-Host "ðŸ“Š Buscando mejor modelo en MLflow..." -ForegroundColor Cyan
Write-Host ""

$pythonScript = @"
import mlflow
import shutil
from pathlib import Path
import json

# Configurar MLflow
mlflow.set_tracking_uri('file:./mlruns')
mlflow.set_experiment('deteccion_arritmias_ecg')

# Buscar experimento
try:
    exp = mlflow.get_experiment_by_name('deteccion_arritmias_ecg')
    if not exp:
        print('ERROR:No hay experimentos registrados')
        print('HINT:Ejecuta primero: python deteccionarritmias.py')
        exit(1)
except Exception as e:
    print(f'ERROR:Error al buscar experimento: {e}')
    exit(1)

# Buscar mejor modelo por F1-Score de clase V
try:
    runs = mlflow.search_runs(
        experiment_ids=[exp.experiment_id],
        filter_string='',
        order_by=['metrics.test_f1_V DESC'],
        max_results=1
    )
    
    if runs.empty:
        print('ERROR:No hay runs registrados en MLflow')
        print('HINT:Ejecuta primero: python deteccionarritmias.py')
        exit(1)
    
    best_run = runs.iloc[0]
    
    # Mostrar informaciÃ³n del mejor modelo
    print(f'SUCCESS:Mejor modelo encontrado')
    print(f'RUN_ID:{best_run.run_id}')
    
    # Intentar obtener mÃ©tricas (pueden no existir todas)
    f1_v = best_run.get('metrics.test_f1_V', 0.0) if 'metrics.test_f1_V' in best_run else 0.0
    accuracy = best_run.get('metrics.test_accuracy', 0.0) if 'metrics.test_accuracy' in best_run else 0.0
    precision_v = best_run.get('metrics.test_precision_V', 0.0) if 'metrics.test_precision_V' in best_run else 0.0
    recall_v = best_run.get('metrics.test_recall_V', 0.0) if 'metrics.test_recall_V' in best_run else 0.0
    
    print(f'F1_V:{f1_v:.4f}')
    print(f'ACCURACY:{accuracy:.4f}')
    print(f'PRECISION_V:{precision_v:.4f}')
    print(f'RECALL_V:{recall_v:.4f}')
    
    # Guardar mÃ©tricas en archivo JSON para el commit
    metrics_info = {
        'run_id': best_run.run_id,
        'f1_v': float(f1_v),
        'accuracy': float(accuracy),
        'precision_v': float(precision_v),
        'recall_v': float(recall_v)
    }
    
    with open('.mlflow_deploy_metrics.json', 'w') as f:
        json.dump(metrics_info, f, indent=2)
    
except Exception as e:
    print(f'ERROR:Error al buscar runs: {e}')
    exit(1)

# Copiar modelo al directorio de producciÃ³n
try:
    # Buscar el modelo en artifacts
    model_src = Path(f'mlruns/{exp.experiment_id}/{best_run.run_id}/artifacts/models/model_v7.keras')
    model_dst = Path('models/ecg_nv_cnn/model_v7.keras')
    
    if not model_src.exists():
        # Intentar ruta alternativa
        model_src = Path(f'mlruns/{exp.experiment_id}/{best_run.run_id}/artifacts/model/model_v7.keras')
    
    if model_src.exists():
        model_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(model_src, model_dst)
        print(f'COPY_SUCCESS:Modelo copiado a {model_dst}')
    else:
        print(f'ERROR:Modelo no encontrado en {model_src}')
        print('HINT:Verifica que el entrenamiento guardÃ³ el modelo correctamente')
        exit(1)
        
except Exception as e:
    print(f'ERROR:Error al copiar modelo: {e}')
    exit(1)

print('MLFLOW_DONE:Proceso MLflow completado exitosamente')
"@

# Ejecutar script Python
$output = python -c $pythonScript 2>&1

# Procesar salida
$success = $false
$runId = ""
$f1Score = ""
$accuracy = ""

foreach ($line in $output) {
    if ($line -match "^ERROR:(.+)") {
        Write-Host "âŒ $($matches[1])" -ForegroundColor Red
        exit 1
    }
    elseif ($line -match "^HINT:(.+)") {
        Write-Host "ðŸ’¡ $($matches[1])" -ForegroundColor Yellow
    }
    elseif ($line -match "^SUCCESS:(.+)") {
        Write-Host "âœ… $($matches[1])" -ForegroundColor Green
    }
    elseif ($line -match "^RUN_ID:(.+)") {
        $runId = $matches[1]
        Write-Host "   Run ID: $runId" -ForegroundColor Gray
    }
    elseif ($line -match "^F1_V:(.+)") {
        $f1Score = $matches[1]
        Write-Host "   F1-Score V: $f1Score" -ForegroundColor Green
    }
    elseif ($line -match "^ACCURACY:(.+)") {
        $accuracy = $matches[1]
        Write-Host "   Accuracy: $accuracy" -ForegroundColor Green
    }
    elseif ($line -match "^PRECISION_V:(.+)") {
        Write-Host "   Precision V: $($matches[1])" -ForegroundColor Gray
    }
    elseif ($line -match "^RECALL_V:(.+)") {
        Write-Host "   Recall V: $($matches[1])" -ForegroundColor Gray
    }
    elseif ($line -match "^COPY_SUCCESS:(.+)") {
        Write-Host "âœ… $($matches[1])" -ForegroundColor Green
    }
    elseif ($line -match "^MLFLOW_DONE:") {
        $success = $true
    }
}

if (-not $success) {
    Write-Host ""
    Write-Host "âŒ Error al procesar MLflow. Abortando despliegue." -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================================================
# PASO 2: Preparar archivos para Hugging Face
# ============================================================================
Write-Host "ðŸ“¦ Preparando archivos para Hugging Face..." -ForegroundColor Cyan
Write-Host ""

try {
    # Copiar README especial para HF (se convierte en README.md)
    if (Test-Path "README_HF.md") {
        Copy-Item README_HF.md README.md -Force
        Write-Host "âœ… README.md actualizado" -ForegroundColor Green
    }
    
    # Copiar Dockerfile especial para HF
    if (Test-Path "Dockerfile.hf") {
        Copy-Item Dockerfile.hf Dockerfile -Force
        Write-Host "âœ… Dockerfile actualizado" -ForegroundColor Green
    }
    
    Write-Host ""
}
catch {
    Write-Host "âŒ Error al preparar archivos: $_" -ForegroundColor Red
    exit 1
}

# ============================================================================
# PASO 3: Verificar que el remoto de HF estÃ¡ configurado
# ============================================================================
Write-Host "ðŸ”— Verificando configuraciÃ³n de Git..." -ForegroundColor Cyan
Write-Host ""

$hfRemote = git remote get-url hf 2>$null

if (-not $hfRemote) {
    Write-Host "âš ï¸  Remoto 'hf' no configurado" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Configura tu Space de Hugging Face:" -ForegroundColor White
    Write-Host "  git remote add hf https://huggingface.co/spaces/TU_USUARIO/TU_SPACE" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "O ejecuta el script deploy-to-hf.ps1 primero para configuraciÃ³n inicial" -ForegroundColor Yellow
    exit 1
}

Write-Host "âœ… Remoto HF configurado: $hfRemote" -ForegroundColor Green
Write-Host ""

# ============================================================================
# PASO 4: Commit y Push a Hugging Face
# ============================================================================
Write-Host "ðŸ“¤ Desplegando a Hugging Face..." -ForegroundColor Cyan
Write-Host ""

# Leer mÃ©tricas del archivo JSON
$metricsFile = ".mlflow_deploy_metrics.json"
if (Test-Path $metricsFile) {
    $metrics = Get-Content $metricsFile | ConvertFrom-Json
    $commitMessage = "Deploy: MLflow model (F1-V: $($metrics.f1_v.ToString('0.0000')), Acc: $($metrics.accuracy.ToString('0.0000')))"
    Remove-Item $metricsFile -Force
}
else {
    $commitMessage = "Deploy: Updated model from MLflow"
}

try {
    # Agregar archivos
    git add models/ecg_nv_cnn/model_v7.keras
    git add README.md
    git add Dockerfile
    
    # Commit
    Write-Host "Creando commit: $commitMessage" -ForegroundColor Gray
    git commit -m $commitMessage
    
    # Push a Hugging Face
    Write-Host "Subiendo a Hugging Face (esto puede tardar varios minutos)..." -ForegroundColor Yellow
    git push hf main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—" -ForegroundColor Green
        Write-Host "â•‘              âœ… DESPLIEGUE COMPLETADO                       â•‘" -ForegroundColor Green
        Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Green
        Write-Host ""
        Write-Host "ðŸ“Š Modelo desplegado:" -ForegroundColor Cyan
        Write-Host "   F1-Score V: $f1Score" -ForegroundColor White
        Write-Host "   Accuracy: $accuracy" -ForegroundColor White
        Write-Host ""
        Write-Host "ðŸ”— Accede a tu Space:" -ForegroundColor Cyan
        Write-Host "   $hfRemote" -ForegroundColor White
        Write-Host ""
        Write-Host "â³ El build puede tardar 5-10 minutos" -ForegroundColor Yellow
        Write-Host "   Monitorea el progreso en Hugging Face" -ForegroundColor Yellow
        Write-Host ""
    }
    else {
        Write-Host ""
        Write-Host "âŒ Error al hacer push a Hugging Face" -ForegroundColor Red
        Write-Host "Verifica tu conexiÃ³n y autenticaciÃ³n" -ForegroundColor Yellow
        exit 1
    }
}
catch {
    Write-Host ""
    Write-Host "âŒ Error durante el despliegue: $_" -ForegroundColor Red
    exit 1
}

# ============================================================================
# PASO 5: Limpiar archivos temporales
# ============================================================================
Write-Host "ðŸ§¹ Limpiando archivos temporales..." -ForegroundColor Cyan

# Restaurar archivos originales (opcional)
# git checkout README.md Dockerfile

Write-Host "âœ… Despliegue finalizado exitosamente" -ForegroundColor Green
Write-Host ""

