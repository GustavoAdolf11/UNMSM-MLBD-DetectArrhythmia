# Script automatizado para desplegar en Hugging Face Spaces
# Ejecutar desde el directorio raíz del proyecto

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Despliegue en Hugging Face Spaces" -ForegroundColor Cyan
Write-Host "  ECG Arrhythmia Detection API" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Paso 1: Verificar que estamos en el directorio correcto
if (-not (Test-Path "src")) {
    Write-Host "❌ Error: No se encuentra el directorio 'src'" -ForegroundColor Red
    Write-Host "   Asegúrate de ejecutar este script desde el directorio raíz del proyecto" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Directorio verificado" -ForegroundColor Green

# Paso 2: Verificar que existe el modelo
if (-not (Test-Path "models/ecg_nv_cnn/model_v7.keras")) {
    Write-Host "❌ Error: No se encuentra el modelo en models/ecg_nv_cnn/model_v7.keras" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Modelo encontrado" -ForegroundColor Green

# Paso 3: Preparar archivos para Hugging Face
Write-Host ""
Write-Host "📋 Preparando archivos para Hugging Face..." -ForegroundColor Cyan

# Copiar README especial
Copy-Item -Path "README_HF.md" -Destination "README.md" -Force
Write-Host "✓ README.md actualizado" -ForegroundColor Green

# Copiar Dockerfile especial
Copy-Item -Path "Dockerfile.hf" -Destination "Dockerfile" -Force
Write-Host "✓ Dockerfile actualizado" -ForegroundColor Green

# Paso 4: Verificar Git
Write-Host ""
Write-Host "🔍 Verificando Git..." -ForegroundColor Cyan

if (-not (Test-Path ".git")) {
    Write-Host "📦 Inicializando repositorio Git..." -ForegroundColor Yellow
    git init
    Write-Host "✓ Repositorio Git inicializado" -ForegroundColor Green
} else {
    Write-Host "✓ Repositorio Git existente" -ForegroundColor Green
}

# Paso 5: Verificar Git LFS (para archivos grandes)
Write-Host ""
Write-Host "🔍 Verificando Git LFS..." -ForegroundColor Cyan

$gitLfsInstalled = $false
$gitLfsCheck = $null
try {
    $gitLfsCheck = git lfs version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $gitLfsInstalled = $true
        Write-Host "✓ Git LFS instalado" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠ Git LFS no instalado" -ForegroundColor Yellow
    Write-Host "  Si tu modelo pesa más de 10MB, necesitarás Git LFS" -ForegroundColor Yellow
    Write-Host "  Descarga desde: https://git-lfs.github.com/" -ForegroundColor Yellow
}

if (-not $gitLfsInstalled) {
    Write-Host "⚠ Git LFS no instalado" -ForegroundColor Yellow
    Write-Host "  Si tu modelo pesa más de 10MB, necesitarás Git LFS" -ForegroundColor Yellow
    Write-Host "  Descarga desde: https://git-lfs.github.com/" -ForegroundColor Yellow
}

# Verificar tamaño del modelo
$modelSize = (Get-Item "models/ecg_nv_cnn/model_v7.keras").Length / 1MB
Write-Host "  Tamaño del modelo: $([math]::Round($modelSize, 2)) MB" -ForegroundColor White

if ($modelSize -gt 10 -and $gitLfsInstalled) {
    Write-Host "📦 Configurando Git LFS para el modelo..." -ForegroundColor Yellow
    git lfs install
    git lfs track "models/**/*.keras"
    git lfs track "*.h5"
    git add .gitattributes
    Write-Host "✓ Git LFS configurado" -ForegroundColor Green
} elseif ($modelSize -gt 10 -and -not $gitLfsInstalled) {
    Write-Host ""
    Write-Host "⚠ ADVERTENCIA: Tu modelo pesa más de 10MB" -ForegroundColor Yellow
    Write-Host "  Necesitas instalar Git LFS antes de continuar" -ForegroundColor Yellow
    Write-Host "  1. Descarga Git LFS: https://git-lfs.github.com/" -ForegroundColor Yellow
    Write-Host "  2. Instálalo" -ForegroundColor Yellow
    Write-Host "  3. Vuelve a ejecutar este script" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "¿Deseas continuar de todos modos? (s/N)"
    if ($continue -ne "s" -and $continue -ne "S") {
        exit 1
    }
}

# Paso 6: Solicitar información de Hugging Face
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Configuración de Hugging Face" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para continuar, necesitas:" -ForegroundColor Yellow
Write-Host "  1. Una cuenta en Hugging Face (gratis): https://huggingface.co/join" -ForegroundColor White
Write-Host "  2. Crear un Space con SDK=Docker: https://huggingface.co/spaces" -ForegroundColor White
Write-Host "  3. Un token de acceso: https://huggingface.co/settings/tokens" -ForegroundColor White
Write-Host ""

$hfUsername = Read-Host "Ingresa tu nombre de usuario de Hugging Face"
$hfSpaceName = Read-Host "Ingresa el nombre de tu Space (ej: ecg-arrhythmia-detection)"

# Paso 7: Configurar Git remote
Write-Host ""
Write-Host "🔗 Configurando conexión con Hugging Face..." -ForegroundColor Cyan

$hfUrl = "https://huggingface.co/spaces/$hfUsername/$hfSpaceName"

# Verificar si el remote ya existe
$existingRemote = git remote get-url hf 2>$null
if ($existingRemote) {
    Write-Host "⚠ Remote 'hf' ya existe: $existingRemote" -ForegroundColor Yellow
    $update = Read-Host "¿Deseas actualizarlo? (S/n)"
    if ($update -ne "n" -and $update -ne "N") {
        git remote remove hf
        git remote add hf $hfUrl
        Write-Host "✓ Remote 'hf' actualizado" -ForegroundColor Green
    }
} else {
    git remote add hf $hfUrl
    Write-Host "✓ Remote 'hf' configurado" -ForegroundColor Green
}

# Paso 8: Commit de cambios
Write-Host ""
Write-Host "📝 Preparando commit..." -ForegroundColor Cyan

git add .
$commitMsg = Read-Host "Mensaje del commit (Enter para usar mensaje por defecto)"
if ([string]::IsNullOrWhiteSpace($commitMsg)) {
    $commitMsg = "Deploy ECG Arrhythmia Detection API to Hugging Face"
}

git commit -m $commitMsg
Write-Host "✓ Commit creado" -ForegroundColor Green

# Paso 9: Push a Hugging Face
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Listo para desplegar" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "URL del Space: $hfUrl" -ForegroundColor White
Write-Host "URL de la API: https://$hfUsername-$hfSpaceName.hf.space" -ForegroundColor White
Write-Host ""
Write-Host "Cuando hagas push, Git te pedirá:" -ForegroundColor Yellow
Write-Host "  Username: $hfUsername" -ForegroundColor White
Write-Host "  Password: [tu token de acceso de Hugging Face]" -ForegroundColor White
Write-Host ""

$doPush = Read-Host "¿Deseas hacer push ahora? (S/n)"
if ($doPush -ne "n" -and $doPush -ne "N") {
    Write-Host ""
    Write-Host "🚀 Desplegando a Hugging Face..." -ForegroundColor Cyan
    Write-Host ""
    
    # Detectar la rama actual
    $currentBranch = git branch --show-current
    
    # Push a main (Hugging Face usa main)
    if ($currentBranch -eq "main") {
        git push hf main
    } else {
        git push hf "$($currentBranch):main"
    }
    
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "  ✓ Despliegue iniciado" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Monitorea el progreso en:" -ForegroundColor Cyan
    Write-Host "   $hfUrl" -ForegroundColor White
    Write-Host ""
    Write-Host "⏳ El build tardará 5-10 minutos la primera vez" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Una vez que esté listo, tu API estará disponible en:" -ForegroundColor Cyan
    Write-Host "   https://$hfUsername-$hfSpaceName.hf.space/docs" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "📝 Para desplegar manualmente más tarde, ejecuta:" -ForegroundColor Cyan
    Write-Host "   git push hf main" -ForegroundColor White
    Write-Host ""
}

Write-Host "✓ Proceso completado" -ForegroundColor Green
Write-Host ""
