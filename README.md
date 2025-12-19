---
title: ECG Arrhythmia Detection API
emoji: 💓
colorFrom: red
colorTo: pink
sdk: docker
pinned: false
license: mit
---

# ECG Arrhythmia Detection API 💓

API REST para detección de arritmias cardíacas usando Deep Learning (CNN) sobre señales ECG con **trazabilidad MLOps completa**.

## 🚀 Características

- **Detección automática** de arritmias ventriculares (PVC) en señales ECG
- **Modelo versionado** con MLflow para trazabilidad completa
- **Selección automática** del mejor modelo según métricas de validación
- **Arquitectura limpia** con Domain-Driven Design (DDD)
- **Procesamiento robusto** con filtros digitales y detección de picos R
- **RuleGuard** para reducir falsos positivos basado en intervalos RR
- **API REST** con FastAPI y documentación Swagger automática

## 📊 Modelo en Producción

Este Space despliega automáticamente el **mejor modelo entrenado** según F1-Score de clase V (arritmias ventriculares) desde MLflow.

**Métricas del modelo desplegado:**
- 🎯 **F1-Score V:** Ver logs de build (objetivo: >0.85)
- 📈 **Accuracy:** Ver logs de build (objetivo: >0.98)
- 🔬 **Validado en:** MIT-BIH Arrhythmia Database
- ⚡ **Inferencia:** ~50ms por latido en CPU

## 📋 Tipos de Arritmias

- **N (Normal)**: Latidos normales supraventriculares
- **V (Ventricular)**: Contracciones ventriculares prematuras (PVC)

## 🔧 Uso de la API

### Endpoint de Salud
```bash
GET /health
```

### Predicción de Arritmias
```bash
POST /api/v1/predictions/
```

**Requisitos de la señal:**
- Mínimo 3600 muestras (10 segundos a 360 Hz)
- Frecuencia de muestreo: 360 Hz (recomendado)
- Derivación: MLII (por defecto)

**Ejemplo de solicitud:**
```json
{
  "signal_data": [0.1, 0.15, 0.2, ...],  // 3600+ valores
  "sampling_rate": 360,
  "derivation": "MLII",
  "patient_id": "PATIENT001",
  "apply_ruleguard": true
}
```

**Ejemplo de respuesta:**
```json
{
  "prediction_id": "uuid",
  "timestamp": "2025-12-10T12:00:00",
  "overall_arrhythmia_type": "N",
  "confidence": 0.95,
  "risk_level": "LOW",
  "total_beats_detected": 12,
  "beat_predictions": [
    {
      "beat_index": 0,
      "position_sample": 180,
      "arrhythmia_type": "N",
      "confidence": 0.96,
      "rr_previous": 0.8
    }
  ]
}
```

## 📚 Documentación

Accede a la documentación interactiva Swagger en:
```
https://your-space-name.hf.space/docs
```

## 🔬 Trazabilidad MLOps

Este modelo fue seleccionado automáticamente mediante:

1. **Entrenamiento con múltiples configuraciones**
   - Optimización de hiperparámetros con Optuna
   - Técnicas de balanceo de clases (SMOTE/RandomOverSampler)
   - Focal Loss para clases desbalanceadas

2. **Tracking de experimentos en MLflow**
   - Registro automático de parámetros, métricas y artifacts
   - Comparación de múltiples runs
   - Versionado de modelos

3. **Selección automática por métricas**
   - Ordenado por F1-Score de clase V (arritmias)
   - Validación en datos de test independientes
   - Umbral óptimo determinado por curva Precision-Recall

4. **Deployment con trazabilidad**
   - Historial de Git con métricas de cada modelo desplegado
   - Rollback posible a versiones anteriores
   - Monitoreo de drift en producción (próximamente)

## 🏗️ Arquitectura

- **Domain Layer**: Entidades y reglas de negocio
- **Application Layer**: Casos de uso
- **Infrastructure Layer**: Servicios ML y repositorios
- **Presentation Layer**: API REST con FastAPI
- **MLOps Layer**: MLflow tracking, model registry, drift detection

## 🧠 Modelo

- **Arquitectura**: CNN-1D (7 capas) + Análisis de intervalos RR
- **Input**: Señal ECG (360 muestras @ 360 Hz) + RR intervals
- **Output**: Probabilidad N vs V
- **Dataset**: MIT-BIH Arrhythmia Database
- **Preprocesamiento**: Bandpass filter (0.5-40 Hz) + Robust Z-score normalization
- **Post-procesamiento**: RuleGuard basado en reglas fisiológicas

## 📊 Stack Tecnológico

- **Framework ML**: TensorFlow/Keras 2.15
- **API**: FastAPI + Uvicorn
- **MLOps**: MLflow (tracking + registry)
- **Procesamiento**: SciPy, NumPy
- **Deployment**: Hugging Face Spaces (Docker)
- **Versionado**: Git + Git LFS

## 🔗 Repositorio Completo

Código fuente con MLOps, monitoreo y CI/CD:  
[GitHub Repository](https://github.com/YOUR_USERNAME/YOUR_REPO)

## 📝 Licencia

MIT License - Ver LICENSE para más detalles

---

**Desarrollado con ❤️ usando TensorFlow + FastAPI + MLflow**

- **Arquitectura**: CNN (Convolutional Neural Network)
- **Entrenamiento**: MIT-BIH Arrhythmia Database
- **Precisión**: ~95% en detección de PVCs

## 📄 Licencia

MIT License - ver archivo LICENSE para detalles

## 👥 Autores

Universidad Nacional Mayor de San Marcos - Proyecto de Machine Learning
