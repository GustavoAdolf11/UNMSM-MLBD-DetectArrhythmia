# Arquitectura DDD - ECG Arrhythmia Detection API

## 🏗️ Diagrama de Capas (Clean Architecture + DDD)

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  FastAPI Application (app.py)                       │    │
│  │  ├── Health Router (/health)                        │    │
│  │  └── Predictions Router (/api/v1/predictions)       │    │
│  └─────────────────────────────────────────────────────┘    │
│           │                                                   │
│           │ HTTP Request/Response (Pydantic Schemas)         │
│           ▼                                                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Use Cases (Business Logic)                         │    │
│  │  ├── PredictArrhythmiaUseCase                       │    │
│  │  └── AnalyzeECGSignalUseCase                        │    │
│  └─────────────────────────────────────────────────────┘    │
│           │                                                   │
│           │ DTOs (Data Transfer Objects)                     │
│           ▼                                                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     DOMAIN LAYER (CORE)                      │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │   Entities       │  │  Value Objects   │                 │
│  │  - ECGSignal     │  │  - RRInterval    │                 │
│  │  - Prediction    │  │  - SignalWindow  │                 │
│  └──────────────────┘  └──────────────────┘                 │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Repository Interfaces (Contracts)                  │    │
│  │  - IPredictionRepository                            │    │
│  │  - IModelRepository                                 │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                             ▲
                             │ Depends On (Dependency Inversion)
                             │
┌─────────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Repository Implementations                         │    │
│  │  - ModelRepository (TensorFlow models)              │    │
│  │  - InMemoryPredictionRepository                     │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  ML Services                                        │    │
│  │  - SignalProcessor (filtering, R-peak detection)    │    │
│  │  - ArrhythmiaPredictor (CNN inference)              │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Configuration                                      │    │
│  │  - Settings (env vars)                              │    │
│  │  - Dependency Injection Container                   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
                    External Dependencies
                    - TensorFlow/Keras
                    - NumPy, SciPy
                    - File System (models)
```

## 🔄 Flujo de una Petición de Predicción

```
1. HTTP POST /api/v1/predictions/
   │
   ├─> [Presentation] predictions.py endpoint
   │   - Valida request con Pydantic
   │   - Convierte a PredictionRequestDTO
   │
   ├─> [Application] PredictArrhythmiaUseCase
   │   - Crea entidad ECGSignal (Domain)
   │   - Valida reglas de dominio
   │   │
   │   ├─> [Infrastructure] SignalProcessor
   │   │   - Aplica filtro pasa-banda
   │   │   - Detecta picos R (latidos)
   │   │   - Extrae ventanas y RR intervals
   │   │   - Retorna ProcessedSignalData
   │   │
   │   ├─> [Infrastructure] ArrhythmiaPredictor
   │   │   - Carga modelo ML (ModelRepository)
   │   │   - Prepara inputs (signal windows + RR features)
   │   │   - Ejecuta predicción CNN
   │   │   - Aplica RuleGuard (opcional)
   │   │   - Retorna PredictionResult
   │   │
   │   ├─> [Domain] Crea ArrhythmiaPrediction entity
   │   │   - Aplica validaciones de dominio
   │   │   - Calcula nivel de riesgo
   │   │
   │   └─> [Infrastructure] Persiste en PredictionRepository
   │
   └─> [Presentation] Retorna PredictionResponse
       - Convierte entity a schema Pydantic
       - HTTP 201 Created con JSON
```

## 📦 Principios SOLID Aplicados

### Single Responsibility Principle (SRP)
- Cada clase tiene una única responsabilidad
- `SignalProcessor`: solo procesamiento de señales
- `ArrhythmiaPredictor`: solo predicción ML
- `PredictArrhythmiaUseCase`: solo orquestación del flujo

### Open/Closed Principle (OCP)
- Fácil extender sin modificar código existente
- Nuevos repositorios: implementar `IRepository`
- Nuevos predictores: inyectar en use case

### Liskov Substitution Principle (LSP)
- Interfaces de repositorios son intercambiables
- `InMemoryPredictionRepository` ↔ `PostgresPredictionRepository`

### Interface Segregation Principle (ISP)
- Interfaces pequeñas y específicas
- `IPredictionRepository` vs `IModelRepository`

### Dependency Inversion Principle (DIP)
- **Domain** no depende de infraestructura
- Usa interfaces (contratos abstractos)
- Infraestructura implementa las interfaces del dominio

## 🎯 Ventajas de esta Arquitectura

✅ **Testabilidad**: Fácil crear mocks de repositorios/servicios
✅ **Mantenibilidad**: Cada capa es independiente
✅ **Escalabilidad**: Agregar features sin romper existente
✅ **Flexibilidad**: Cambiar DB/ML framework sin tocar dominio
✅ **Claridad**: Separación clara de responsabilidades

## 🔌 Inyección de Dependencias

```python
# Container (Singleton pattern)
container = DependencyContainer()
  ├─ model_repository: ModelRepository
  ├─ prediction_repository: InMemoryPredictionRepository
  ├─ signal_processor: SignalProcessor
  ├─ predictor_service: ArrhythmiaPredictor
  ├─ predict_arrhythmia_use_case: PredictArrhythmiaUseCase
  └─ analyze_ecg_signal_use_case: AnalyzeECGSignalUseCase

# FastAPI Depends() inyecta automáticamente
@router.post("/predictions/")
async def predict(
    request: PredictionRequest,
    use_case: PredictArrhythmiaUseCase = Depends(get_predict_use_case)
):
    ...
```

## 🧪 Testing Strategy

```
tests/
├── unit/
│   ├── domain/          # Entities, Value Objects
│   ├── application/     # Use Cases con mocks
│   └── infrastructure/  # Services aislados
├── integration/
│   └── api/             # Endpoints E2E
└── fixtures/
    └── sample_signals/  # Datos de prueba
```

## 📚 Referencias

- **DDD**: Domain-Driven Design (Eric Evans)
- **Clean Architecture**: Robert C. Martin
- **Hexagonal Architecture**: Alistair Cockburn
