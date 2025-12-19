# 🚀 Guía MLOps - Detección de Arritmias ECG

Esta guía te ayudará a utilizar las herramientas MLOps implementadas en el proyecto para automatizar el ciclo de vida del modelo de Machine Learning.

## 📋 Tabla de Contenidos

- [¿Qué es MLOps?](#qué-es-mlops)
- [Arquitectura MLOps del Proyecto](#arquitectura-mlops-del-proyecto)
- [Inicio Rápido](#inicio-rápido)
- [Uso de MLflow](#uso-de-mlflow)
- [Pipelines CI/CD](#pipelines-cicd)
- [Monitoreo y Drift Detection](#monitoreo-y-drift-detection)
- [Comparación de Experimentos](#comparación-de-experimentos)
- [Despliegue de Modelos](#despliegue-de-modelos)

---

## 🎯 ¿Qué es MLOps?

MLOps (Machine Learning Operations) automatiza el ciclo completo de vida de los modelos:

1. **Versionado**: Código, datos y modelos
2. **Experimentación**: Tracking de hiperparámetros y métricas
3. **CI/CD**: Entrenamiento y validación automática
4. **Monitoreo**: Detectar degradación del modelo
5. **Reentrenamiento**: Actualizar modelos automáticamente

---

## 🏗️ Arquitectura MLOps del Proyecto

```
┌─────────────────┐
│  Código Fuente  │
│ (deteccionarr..│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  MLflow Track   │◄──── Registra experimentos
│  • Parámetros   │
│  • Métricas     │
│  • Artefactos   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Model Registry  │◄──── Versiona modelos
│ ECG_Arritmias_  │
│     NvsV        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   GitHub        │◄──── CI/CD automático
│   Actions       │
│ • Train         │
│ • Test          │
│ • Deploy        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Monitoring    │◄──── Detecta drift
│ • Data Drift    │
│ • Performance   │
│ • Alerts        │
└─────────────────┘
```

---

## ⚡ Inicio Rápido

### 1. Instalar Dependencias

```powershell
pip install -r requirements-api.txt
```

Esto instalará:
- `mlflow` - Tracking y registro de modelos
- `evidently` - Monitoreo de drift
- `optuna` - Optimización de hiperparámetros (futuro)

### 2. Entrenar con MLflow

```powershell
python deteccionarritmias.py
```

El script ahora automáticamente:
- ✅ Registra todos los hiperparámetros
- ✅ Trackea métricas de entrenamiento
- ✅ Guarda el modelo en MLflow
- ✅ Genera visualizaciones

### 3. Ver Experimentos en MLflow UI

```powershell
# Opción 1: Script automático
.\start_mlflow.ps1

# Opción 2: Comando directo
mlflow ui
```

Luego abre: **http://127.0.0.1:5000**

---

## 📊 Uso de MLflow

### Ver Todos tus Experimentos

En la interfaz de MLflow verás:

```
Experimento: deteccion_arritmias_ecg
├── Run: CNN_v7_20251218_143022
│   ├── Parameters (15)
│   │   ├── deriv_idx: 0
│   │   ├── fs: 360
│   │   ├── use_augment: True
│   │   └── ...
│   ├── Metrics (25)
│   │   ├── test_accuracy: 0.9234
│   │   ├── test_precision_V: 0.8567
│   │   └── ...
│   └── Artifacts
│       ├── model/ (modelo completo)
│       ├── training_curves.png
│       └── ...
└── Run: CNN_v7_20251218_150133
    └── ...
```

### Comparar Experimentos

1. Selecciona múltiples runs (checkbox)
2. Click en "Compare"
3. Visualiza diferencias en:
   - Parámetros
   - Métricas
   - Gráficos lado a lado

### Cargar un Modelo Guardado

```python
import mlflow

# Cargar modelo por Run ID
model = mlflow.keras.load_model("runs:/<RUN_ID>/model")

# O por nombre y versión
model = mlflow.pyfunc.load_model("models:/ECG_Arritmias_NvsV/1")
```

### Buscar el Mejor Modelo

```python
import mlflow

mlflow.set_tracking_uri("file:./mlruns")
experiment = mlflow.get_experiment_by_name("deteccion_arritmias_ecg")

# Buscar runs ordenados por F1 score
runs = mlflow.search_runs(
    experiment_ids=[experiment.experiment_id],
    order_by=["metrics.test_f1_V DESC"],
    max_results=5
)

print("Top 5 modelos:")
print(runs[['run_id', 'metrics.test_f1_V', 'metrics.test_accuracy']])
```

---

## 🤖 Pipelines CI/CD

### Pipeline de Entrenamiento (`.github/workflows/mlops-train.yml`)

**Se ejecuta cuando:**
- Push a `main` o `develop`
- Pull Request
- Manualmente desde GitHub
- Cada domingo a las 2 AM (reentrenamiento semanal)

**Pasos:**
1. ✅ Instala dependencias
2. ✅ Verifica datos MIT-BIH
3. ✅ Ejecuta tests
4. ✅ Entrena modelo
5. ✅ Valida métricas mínimas
6. ✅ Archiva artefactos

**Umbrales de validación:**
```yaml
accuracy >= 0.80
precision_V >= 0.75
recall_V >= 0.75
```

### Pipeline de Monitoreo (`.github/workflows/monitoring.yml`)

**Se ejecuta:**
- Cada lunes a las 3 AM
- Manualmente desde GitHub

**Detecta:**
- Data drift en features
- Cambios en distribuciones
- Degradación del modelo

### Ejecutar Manualmente

1. Ve a tu repositorio en GitHub
2. Click en "Actions"
3. Selecciona el workflow
4. Click en "Run workflow"

---

## 🔍 Monitoreo y Drift Detection

### ¿Qué es Data Drift?

Cuando la distribución de datos de producción cambia respecto al entrenamiento, el modelo puede degradarse.

### Usar el Detector de Drift

```python
from monitoring.drift_detector import ECGDriftDetector
import pandas as pd

# Cargar datos de referencia (baseline)
reference_data = pd.read_csv('reference_features.csv')

# Datos actuales de producción
current_data = pd.read_csv('production_features.csv')

# Detectar drift
detector = ECGDriftDetector()
detector.load_reference_data(reference_data)
results = detector.detect_drift(current_data)

if results['drift_detected']:
    print(f"⚠️  Drift detectado en: {results['drifted_features']}")
    # Trigger reentrenamiento
```

### Monitoreo Continuo

El workflow `monitoring.yml` ejecuta automáticamente:

```bash
python monitoring/drift_detector.py
```

Genera:
- `drift_report_<timestamp>.html` - Visualización completa
- `drift_summary_<timestamp>.json` - Resumen ejecutable
- `drift_alerts.log` - Log de alertas

---

## 🔬 Comparación de Experimentos

### Ejemplo: Probar diferentes configuraciones

**Experimento 1: Sin augmentation**
```python
# En deteccionarritmias.py
USE_AUGMENT = False
```

**Experimento 2: Con augmentation**
```python
USE_AUGMENT = True
```

**Experimento 3: Sin RuleGuard**
```python
USE_RULEGUARD = False
```

Después de entrenar los 3, en MLflow UI:
1. Selecciona los 3 runs
2. Click "Compare"
3. Observa:
   - `test_f1_V`: ¿Cuál tiene mejor F1?
   - `test_FP`: ¿Cuál reduce falsos positivos?
   - Training time

### Tags Personalizados

Agrega tags para organizar experimentos:

```python
mlflow.set_tags({
    "developer": "tu_nombre",
    "experiment_type": "hyperparameter_tuning",
    "notes": "Probando focal loss con alpha=0.4"
})
```

---

## 🚀 Despliegue de Modelos

### Promover Modelo a Producción

```python
import mlflow

client = mlflow.tracking.MlflowClient()

# Obtener última versión del modelo
model_name = "ECG_Arritmias_NvsV"
latest_version = client.get_latest_versions(model_name)[0]

# Promover a producción
client.transition_model_version_stage(
    name=model_name,
    version=latest_version.version,
    stage="Production"
)
```

### Servir Modelo con MLflow

```powershell
# Servir el modelo en producción
mlflow models serve -m "models:/ECG_Arritmias_NvsV/Production" -p 5001
```

Luego hacer predicciones:

```python
import requests
import json

data = {
    "instances": [{
        "sig": [...],  # 360 valores
        "rr": [0.8, 0.82, 1.025]
    }]
}

response = requests.post(
    "http://127.0.0.1:5001/invocations",
    json=data,
    headers={"Content-Type": "application/json"}
)

print(response.json())
```

---

## 📈 Métricas Registradas

### Hiperparámetros
- `deriv_idx`, `fs`, `win`
- `use_augment`, `use_ruleguard`
- `focal_gamma`, `focal_alpha`
- `batch_size`, `epochs_max`
- `target_prec`, `target_rec`

### Métricas de Datos
- `train_samples_total`, `test_samples_total`
- `train_V_balanced`, `train_N_balanced`
- `balance_ratio`

### Métricas de Entrenamiento (por época)
- `train_loss`, `train_accuracy`, `train_pr_auc`
- `val_loss`, `val_accuracy`, `val_pr_auc`

### Métricas de Test
- `test_accuracy`
- `test_precision_V`, `test_recall_V`, `test_f1_V`
- `test_precision_N`, `test_recall_N`, `test_f1_N`
- `test_TN`, `test_FP`, `test_FN`, `test_TP`

### Artefactos
- `model/` - Modelo completo (Keras)
- `training_curves.png` - Gráficas de entrenamiento
- `models/model_v7.keras` - Archivo .keras
- `metadata/meta_v7.json` - Metadatos
- `metrics/history_v7.csv` - Historial completo

---

## 🛠️ Comandos Útiles

### MLflow CLI

```powershell
# Ver experimentos
mlflow experiments list

# Ver runs de un experimento
mlflow runs list --experiment-id 0

# Eliminar un run
mlflow runs delete --run-id <RUN_ID>

# Buscar runs
mlflow runs search --experiment-id 0 --filter "metrics.test_f1_V > 0.85"
```

### Python API

```python
import mlflow

# Configurar tracking
mlflow.set_tracking_uri("file:./mlruns")

# Listar experimentos
experiments = mlflow.search_experiments()

# Buscar runs
runs = mlflow.search_runs(
    filter_string="metrics.test_accuracy > 0.90"
)

# Obtener métrica específica
run = mlflow.get_run("<RUN_ID>")
accuracy = run.data.metrics["test_accuracy"]
```

---

## 🔄 Flujo de Trabajo Recomendado

### 1. Experimentación Local

```bash
# Modificar hiperparámetros en deteccionarritmias.py
# Ejecutar entrenamiento
python deteccionarritmias.py

# Ver resultados
mlflow ui
```

### 2. Comparar y Seleccionar

En MLflow UI:
- Comparar experimentos
- Identificar mejor modelo
- Anotar insights

### 3. Commit y Push

```bash
git add .
git commit -m "Experimento: nuevo focal alpha=0.4"
git push
```

### 4. CI/CD Automático

GitHub Actions:
- Entrena automáticamente
- Valida métricas
- Archiva artefactos

### 5. Monitoreo Continuo

Semanalmente:
- Detecta drift
- Evalúa rendimiento
- Trigger reentrenamiento si es necesario

---

## 🐛 Troubleshooting

### No veo mis experimentos en MLflow UI

```powershell
# Verifica que la carpeta mlruns existe
ls mlruns/

# Asegúrate de ejecutar mlflow ui en el directorio correcto
cd e:\proyectoML - copia - copia
mlflow ui
```

### Error: "Experiment not found"

```python
# Verificar nombre del experimento
import mlflow
experiments = mlflow.search_experiments()
print([e.name for e in experiments])
```

### GitHub Actions falla en "Verificar datos MIT-BIH"

Los datos MIT-BIH son grandes y no deben estar en Git. Opciones:

1. **Usar DVC** (recomendado):
```bash
dvc init
dvc add mit-bih/
git add mit-bih.dvc .dvc/
```

2. **Descargar en CI** (más lento):
Agregar step de descarga en workflow.

---

## 📚 Recursos Adicionales

- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Evidently AI Docs](https://docs.evidentlyai.com/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Optuna](https://optuna.readthedocs.io/)

---

## 🎯 Próximos Pasos

1. **Hyperparameter Tuning con Optuna**
   - Optimización automática de hiperparámetros
   - Integración con MLflow

2. **A/B Testing**
   - Comparar modelos en producción
   - Enrutamiento inteligente

3. **Model Serving en Cloud**
   - Despliegue en Azure ML / AWS SageMaker
   - Escalado automático

4. **Dashboards de Monitoreo**
   - Grafana + Prometheus
   - Alertas en tiempo real

---

**¿Preguntas?** Consulta el archivo [ARCHITECTURE.md](ARCHITECTURE.md) para más detalles sobre la arquitectura del proyecto.
