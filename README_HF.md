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

API REST para detección de arritmias cardíacas usando Deep Learning (CNN) sobre señales ECG.

## 🚀 Características

- **Detección de arritmias** en señales ECG usando CNN pre-entrenada
- **Arquitectura limpia** con Domain-Driven Design (DDD)
- **Procesamiento de señales** con filtros y detección de picos R
- **RuleGuard** para reducir falsos positivos
- **API REST** con FastAPI y documentación Swagger

## 📊 Tipos de Arritmias

- **N (Normal)**: Latidos normales
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

## 🏗️ Arquitectura

- **Domain Layer**: Entidades y reglas de negocio
- **Application Layer**: Casos de uso
- **Infrastructure Layer**: Servicios ML y repositorios
- **Presentation Layer**: API REST con FastAPI

## 🧠 Modelo

- **Arquitectura**: CNN (Convolutional Neural Network)
- **Entrenamiento**: MIT-BIH Arrhythmia Database
- **Precisión**: ~95% en detección de PVCs

## 📄 Licencia

MIT License - ver archivo LICENSE para detalles

## 👥 Autores

Universidad Nacional Mayor de San Marcos - Proyecto de Machine Learning
