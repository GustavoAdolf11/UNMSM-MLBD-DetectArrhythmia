# Estructura Completa del Proyecto - Backend API

```
proyectoML/
│
├── 📁 src/                                    # Código fuente (Arquitectura DDD)
│   │
│   ├── 📁 domain/                             # Capa de Dominio (Core Business Logic)
│   │   ├── __init__.py
│   │   ├── 📁 entities/                       # Entidades del dominio
│   │   │   ├── __init__.py
│   │   │   ├── ecg_signal.py                  # Entidad: Señal ECG
│   │   │   └── arrhythmia_prediction.py       # Entidad: Predicción de arritmia
│   │   ├── 📁 value_objects/                  # Objetos de valor (inmutables)
│   │   │   ├── __init__.py
│   │   │   ├── rr_interval.py                 # VO: Intervalos RR
│   │   │   └── signal_window.py               # VO: Ventana de señal
│   │   └── 📁 repositories/                   # Interfaces de repositorios
│   │       ├── __init__.py
│   │       ├── prediction_repository.py       # Interface: Repositorio de predicciones
│   │       └── model_repository.py            # Interface: Repositorio de modelos
│   │
│   ├── 📁 application/                        # Capa de Aplicación (Use Cases)
│   │   ├── __init__.py
│   │   ├── 📁 use_cases/                      # Casos de uso (orquestación)
│   │   │   ├── __init__.py
│   │   │   ├── predict_arrhythmia_use_case.py # UC: Predecir arritmias
│   │   │   └── analyze_ecg_signal_use_case.py # UC: Analizar señal ECG
│   │   └── 📁 dtos/                           # Data Transfer Objects
│   │       ├── __init__.py
│   │       ├── prediction_dto.py              # DTOs de predicción
│   │       └── ecg_signal_dto.py              # DTOs de señal ECG
│   │
│   ├── 📁 infrastructure/                     # Capa de Infraestructura (Implementaciones)
│   │   ├── __init__.py
│   │   ├── 📁 ml/                             # Servicios de Machine Learning
│   │   │   ├── __init__.py
│   │   │   ├── signal_processor.py            # Procesamiento de señales ECG
│   │   │   └── arrhythmia_predictor.py        # Predictor CNN
│   │   ├── 📁 repositories/                   # Implementaciones de repositorios
│   │   │   ├── __init__.py
│   │   │   ├── model_repository.py            # Repo: Modelos ML (TensorFlow)
│   │   │   └── in_memory_prediction_repository.py  # Repo: Predicciones (in-memory)
│   │   └── 📁 config/                         # Configuración
│   │       ├── __init__.py
│   │       ├── settings.py                    # Settings (Pydantic)
│   │       └── dependencies.py                # Dependency Injection Container
│   │
│   ├── 📁 presentation/                       # Capa de Presentación (API REST)
│   │   ├── __init__.py
│   │   ├── app.py                             # FastAPI Application Factory
│   │   ├── 📁 api/                            # Endpoints/Routers
│   │   │   ├── __init__.py
│   │   │   ├── predictions.py                 # Endpoints: Predicciones
│   │   │   └── health.py                      # Endpoints: Health check
│   │   └── 📁 schemas/                        # Pydantic Schemas (validación)
│   │       ├── __init__.py
│   │       └── prediction_schemas.py          # Schemas de request/response
│   │
│   └── 📁 shared/                             # Utilidades compartidas
│       ├── __init__.py
│       └── exceptions.py                      # Excepciones custom
│
├── 📁 models/                                 # Modelos ML entrenados
│   └── 📁 ecg_nv_cnn/
│       ├── model_v7.keras                     # Modelo Keras/TensorFlow
│       ├── meta_v7.json                       # Metadatos del modelo
│       └── saved_model_v7/                    # SavedModel format
│
├── 📁 examples/                               # Ejemplos de uso
│   ├── api_usage.py                           # Ejemplo Python (requests)
│   └── curl_examples.sh                       # Ejemplos curl
│
├── 📁 tests/                                  # Tests (estructura para futuros tests)
│
├── 📁 mit-bih/                                # Dataset MIT-BIH (datos de entrenamiento)
│
├── 📄 main.py                                 # Punto de entrada de la API
├── 📄 deteccionarritmias.py                   # Script de entrenamiento original
│
├── 📄 requirements-api.txt                    # Dependencias de la API
├── 📄 requirements.txt                        # Dependencias completas
├── 📄 requirements-lock.txt                   # Dependencias con versiones fijas
│
├── 📄 .env.example                            # Template de variables de entorno
├── 📄 .gitignore                              # Archivos ignorados por Git
│
├── 📄 Dockerfile                              # Imagen Docker
├── 📄 docker-compose.yml                      # Orquestación Docker
│
├── 📄 start-api.ps1                           # Script inicio (Windows PowerShell)
├── 📄 start-api.sh                            # Script inicio (Linux/Mac)
├── 📄 test_api.py                             # Script de validación
│
├── 📄 README.md                               # README original
├── 📄 README-API.md                           # Documentación de la API
├── 📄 QUICKSTART.md                           # Guía de inicio rápido
├── 📄 ARCHITECTURE.md                         # Documentación de arquitectura
├── 📄 PROJECT-STRUCTURE.md                    # Este archivo
│
└── 📄 LICENSE                                 # Licencia del proyecto
```

## 📊 Estadísticas del Proyecto

- **Archivos Python**: 37 módulos
- **Capas DDD**: 5 (Domain, Application, Infrastructure, Presentation, Shared)
- **Entidades**: 2 (ECGSignal, ArrhythmiaPrediction)
- **Value Objects**: 2 (RRInterval, SignalWindow)
- **Use Cases**: 2 (Predict, Analyze)
- **Endpoints**: 2 grupos (Health, Predictions)
- **Repositorios**: 2 (Model, Prediction)

## 🔍 Descripción de Archivos Clave

### Core Business Logic (Domain)
- **ecg_signal.py**: Define la entidad ECGSignal con validaciones y comportamientos
- **arrhythmia_prediction.py**: Entidad para predicciones con niveles de riesgo
- **rr_interval.py**: Objeto de valor para intervalos RR entre latidos
- **signal_window.py**: Ventana de señal ECG normalizada

### Application Layer
- **predict_arrhythmia_use_case.py**: Orquesta todo el flujo de predicción
  - Validación → Procesamiento → Predicción → Persistencia
- **analyze_ecg_signal_use_case.py**: Análisis básico sin predicción

### Infrastructure Services
- **signal_processor.py**: 
  - Filtrado pasa-banda
  - Detección de picos R
  - Extracción de ventanas
  - Cálculo de intervalos RR
  
- **arrhythmia_predictor.py**:
  - Carga de modelo CNN
  - Preparación de inputs
  - Inferencia
  - Aplicación de RuleGuard

### API Layer
- **app.py**: Factory de la aplicación FastAPI
  - Configuración CORS
  - Registro de routers
  - Exception handlers
  - Startup events

- **predictions.py**: Endpoint POST /api/v1/predictions/
- **health.py**: Endpoints GET /health y GET /

## 🎯 Flujo de Datos

```
HTTP Request 
    ↓
[Presentation] FastAPI Endpoint
    ↓
[Application] Use Case
    ↓
[Domain] Entities + Validation
    ↓
[Infrastructure] ML Services
    ↓
[Domain] Create Prediction Entity
    ↓
[Infrastructure] Repository Save
    ↓
[Application] Return DTO
    ↓
[Presentation] HTTP Response
```

## 🚀 Comandos Rápidos

```bash
# Iniciar API
python main.py
# o
./start-api.ps1  # Windows
./start-api.sh   # Linux/Mac

# Validar setup
python test_api.py

# Docker
docker-compose up -d

# Ejemplo de uso
python examples/api_usage.py
```

## 📝 Notas de Arquitectura

- **Separation of Concerns**: Cada capa tiene responsabilidades claras
- **Dependency Inversion**: Domain no depende de Infrastructure
- **Testability**: Fácil mockear servicios e inyectar dependencias
- **Scalability**: Agregar features sin modificar código existente
- **Maintainability**: Código organizado y fácil de entender

## 🔧 Próximas Extensiones

Para agregar nuevas features, seguir este patrón:

1. **Nueva Entidad**: `src/domain/entities/new_entity.py`
2. **Nuevo Use Case**: `src/application/use_cases/new_use_case.py`
3. **Nueva Implementación**: `src/infrastructure/services/new_service.py`
4. **Nuevo Endpoint**: `src/presentation/api/new_router.py`
5. **Registrar en app.py**: `app.include_router(new_router)`

Ejemplo: Agregar almacenamiento en PostgreSQL
- Crear `PostgresPredictionRepository` en `infrastructure/repositories/`
- Implementar interface `IPredictionRepository`
- Cambiar inyección en `dependencies.py`
- ¡Sin tocar Domain o Application!
