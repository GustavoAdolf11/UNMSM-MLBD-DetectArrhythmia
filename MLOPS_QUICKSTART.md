# 📋 Quick Start - MLOps

## Instalación Rápida

### 1. Crear y Activar Entorno Virtual

```powershell
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
.\venv\Scripts\Activate.ps1

# Si da error de permisos, ejecuta primero:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Instalar Dependencias

```powershell
# Actualizar pip
python -m pip install --upgrade pip

# Instalar todas las dependencias (incluye MLOps)
pip install -r requirements-api.txt
```

### 3. Entrenar Modelo

```powershell
# Entrenar modelo (automáticamente registra en MLflow)
python deteccionarritmias.py
```

### 4. Ver Experimentos

```powershell
# Ver experimentos en MLflow UI
.\start_mlflow.ps1
# O manualmente: mlflow ui
```

## Ver tus Experimentos

1. Abre: **http://127.0.0.1:5000**
2. Click en experimento "deteccion_arritmias_ecg"
3. Compara runs, métricas y gráficas

## Comandos Clave

```powershell
# Ver MLflow UI
mlflow ui

# Buscar mejor modelo
python -c "import mlflow; print(mlflow.search_runs(order_by=['metrics.test_f1_V DESC']).head())"

# Detectar drift en datos
python monitoring/drift_detector.py
```

## Estructura de Archivos Nuevos

```
proyectoML/
├── mlflow_config.py           # Configuración MLflow
├── start_mlflow.ps1           # Iniciar UI (Windows)
├── monitoring/
│   └── drift_detector.py      # Detector de data drift
├── .github/workflows/
│   ├── mlops-train.yml        # CI/CD entrenamiento
│   └── monitoring.yml         # Monitoreo continuo
├── mlruns/                    # Experimentos MLflow (auto-generado)
└── MLOPS_GUIDE.md            # Guía completa
```

## Qué Cambió en el Código

✅ **deteccionarritmias.py** - Ahora registra automáticamente:
- Todos los hiperparámetros
- Métricas de entrenamiento y test
- Gráficas y artefactos
- Modelo versionado

❌ **NO cambió** - Tu código sigue funcionando igual, solo agregamos tracking.

## Ver Documentación Completa

Lee [MLOPS_GUIDE.md](MLOPS_GUIDE.md) para:
- Comparar experimentos
- Configurar CI/CD
- Monitoreo de drift
- Despliegue de modelos
