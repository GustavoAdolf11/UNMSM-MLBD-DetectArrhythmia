# ECG Arrhythmia Detection API - Backend

API REST desarrollada con **FastAPI** para detectar arritmias cardíacas en señales ECG utilizando Deep Learning (CNN).

## 🏗️ Arquitectura

Este proyecto implementa **Domain-Driven Design (DDD)** con arquitectura limpia (Clean Architecture):

```
src/
├── domain/              # Capa de Dominio (Entities, Value Objects, Repository Interfaces)
│   ├── entities/        # ECGSignal, ArrhythmiaPrediction
│   ├── value_objects/   # RRInterval, SignalWindow
│   └── repositories/    # Interfaces de repositorios
├── application/         # Capa de Aplicación (Use Cases, DTOs)
│   ├── use_cases/       # PredictArrhythmiaUseCase, AnalyzeECGSignalUseCase
│   └── dtos/            # Data Transfer Objects
├── infrastructure/      # Capa de Infraestructura (Implementaciones)
│   ├── ml/              # SignalProcessor, ArrhythmiaPredictor
│   ├── repositories/    # ModelRepository, PredictionRepository
│   └── config/          # Settings, Dependencies
├── presentation/        # Capa de Presentación (API REST)
│   ├── api/             # Endpoints FastAPI
│   └── schemas/         # Pydantic schemas
└── shared/              # Utilidades compartidas (Exceptions)
```

## 🚀 Características

- ✅ **Detección de arritmias** N (Normal) vs V (Ventricular)
- ✅ **Análisis por latido** con intervalos RR y ancho QRS
- ✅ **RuleGuard** para reducir falsos positivos
- ✅ **API RESTful** con FastAPI
- ✅ **Arquitectura limpia** (DDD + Hexagonal)
- ✅ **Inyección de dependencias**
- ✅ **Documentación automática** (Swagger/OpenAPI)
- ✅ **CORS configurado**
- ✅ **Validación con Pydantic**

## 📋 Requisitos

- Python 3.9+
- TensorFlow 2.15
- FastAPI
- Modelo entrenado en `models/ecg_nv_cnn/`

## 🔧 Instalación

### 1. Clonar el repositorio

```bash
git clone <repo-url>
cd proyectoML
```

### 2. Crear entorno virtual

```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements-api.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env según necesidad
```

### 5. Verificar modelo ML

Asegúrate de que exista:
```
models/ecg_nv_cnn/
├── model_v7.keras
└── meta_v7.json
```

## ▶️ Ejecución

### Desarrollo (con hot-reload)

```bash
python main.py
```

O usando uvicorn directamente:

```bash
uvicorn src.presentation.app:app --reload --host 0.0.0.0 --port 8000
```

### Producción

```bash
uvicorn src.presentation.app:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📚 Uso de la API

### Health Check

```bash
GET http://localhost:8000/health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "model_loaded": true,
  "timestamp": "2025-12-10T12:00:00Z"
}
```

### Predicción de Arritmia

```bash
POST http://localhost:8000/api/v1/predictions/
Content-Type: application/json
```

**Request Body:**
```json
{
  "signal_data": [0.1, 0.15, 0.2, ...],  // Mínimo 360 muestras
  "sampling_rate": 360,
  "derivation": "MLII",
  "patient_id": "P001",
  "apply_ruleguard": true
}
```

**Response:**
```json
{
  "prediction_id": "uuid",
  "ecg_signal_id": "uuid",
  "overall_arrhythmia_type": "N",
  "overall_confidence": 0.95,
  "risk_level": "LOW",
  "threshold_used": 0.5,
  "total_beats": 10,
  "normal_beats": 10,
  "ventricular_beats": 0,
  "beat_predictions": [
    {
      "beat_index": 0,
      "position_sample": 180,
      "arrhythmia_type": "N",
      "confidence": 0.96,
      "rr_previous": 0.85,
      "rr_next": 0.83,
      "qrs_width_ms": 95.2
    }
  ],
  "processing_time_ms": 245.3,
  "created_at": "2025-12-10T12:00:00Z",
  "metadata": {}
}
```

## 📖 Documentación Interactiva

Una vez iniciado el servidor, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🧪 Testing con Python

```python
import requests
import numpy as np

# Generar señal de prueba (10 segundos @ 360 Hz)
signal = np.sin(np.linspace(0, 20*np.pi, 3600)).tolist()

response = requests.post(
    "http://localhost:8000/api/v1/predictions/",
    json={
        "signal_data": signal,
        "sampling_rate": 360,
        "apply_ruleguard": True
    }
)

print(response.json())
```

## 🐳 Docker (Opcional)

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.presentation.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build y Run:**
```bash
docker build -t ecg-api .
docker run -p 8000:8000 ecg-api
```

## 📐 Principios DDD Aplicados

### 1. **Domain Layer** (Núcleo)
- **Entities**: `ECGSignal`, `ArrhythmiaPrediction`
- **Value Objects**: `RRInterval`, `SignalWindow` (inmutables)
- **Repository Interfaces**: Contratos sin implementación

### 2. **Application Layer** (Casos de Uso)
- **Use Cases**: Lógica de aplicación pura
- **DTOs**: Transferencia de datos entre capas

### 3. **Infrastructure Layer** (Implementaciones)
- **Repositories**: Implementaciones concretas
- **ML Services**: Procesamiento de señales, predicción
- **Config**: Settings, dependency injection

### 4. **Presentation Layer** (API)
- **FastAPI Routers**: Endpoints REST
- **Pydantic Schemas**: Validación de entrada/salida

## 🔒 Seguridad

- ✅ Validación de entrada con Pydantic
- ✅ Type hints en todo el código
- ✅ Exception handling centralizado
- ⚠️ Implementar autenticación JWT para producción
- ⚠️ Limitar CORS origins en producción

## 🚧 TODOs

- [ ] Agregar autenticación JWT
- [ ] Implementar rate limiting
- [ ] Base de datos (PostgreSQL/MongoDB) para persistencia
- [ ] Tests unitarios e integración
- [ ] Logging estructurado
- [ ] Métricas y monitoring (Prometheus)
- [ ] CI/CD pipeline

## 📝 Licencia

MIT

## 👥 Contribución

Desarrollado con arquitectura limpia y DDD para máxima mantenibilidad y escalabilidad.
