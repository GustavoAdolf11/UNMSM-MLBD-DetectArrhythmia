# 📚 Índice de Documentación - ECG Arrhythmia Detection API

## 🎯 Inicio Rápido

Comienza aquí si quieres poner en marcha el proyecto:

1. **[QUICKSTART.md](QUICKSTART.md)** - Guía de inicio en 3 pasos
   - Instalación local
   - Docker
   - Primeras pruebas

2. **🆕 [MLOPS_QUICKSTART.md](MLOPS_QUICKSTART.md)** - Setup MLOps en 5 minutos ⚡
   - Instalación MLflow
   - Primer entrenamiento con tracking
   - Ver experimentos

## 📖 Documentación Principal

### 🆕 MLOps (Machine Learning Operations)

- **[MLOPS_SUMMARY.md](MLOPS_SUMMARY.md)** 🌟 - Resumen completo de implementación MLOps
  - Qué se implementó
  - Archivos nuevos creados
  - Cómo usar cada funcionalidad
  
- **[MLOPS_QUICKSTART.md](MLOPS_QUICKSTART.md)** - Inicio rápido (5 minutos)
  - Instalación de dependencias
  - Entrenar con tracking automático
  - Ver resultados en MLflow UI
  
- **[MLOPS_GUIDE.md](MLOPS_GUIDE.md)** - Guía completa MLOps (30 minutos)
  - Tracking de experimentos
  - Comparación de modelos
  - CI/CD con GitHub Actions
  - Monitoreo de drift
  - Optimización de hiperparámetros

### Para Usuarios de la API

- **[README-API.md](README-API.md)** - Documentación completa de la API
  - Características
  - Instalación detallada
  - Uso de endpoints
  - Ejemplos Python y curl
  - Despliegue con Docker

### Para Desarrolladores

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Arquitectura y diseño
  - Diagrama de capas (DDD + Clean Architecture)
  - Flujo de peticiones
  - Principios SOLID aplicados
  - Patrones de diseño

- **[PROJECT-STRUCTURE.md](PROJECT-STRUCTURE.md)** - Estructura del proyecto
  - Árbol de directorios completo
  - Descripción de cada módulo
  - Estadísticas del proyecto
  - Cómo extender el código

## 🚀 Scripts y Herramientas

### Ejecución
- **[main.py](main.py)** - Punto de entrada de la aplicación
- **[start-api.ps1](start-api.ps1)** - Script de inicio para Windows
- **[start-api.sh](start-api.sh)** - Script de inicio para Linux/Mac

### Testing y Validación
- **[test_api.py](test_api.py)** - Validación de setup y configuración

### Ejemplos
- **[examples/api_usage.py](examples/api_usage.py)** - Ejemplos con Python requests
- **[examples/curl_examples.sh](examples/curl_examples.sh)** - Ejemplos con curl

## 🐳 Docker

- **[Dockerfile](Dockerfile)** - Imagen Docker de la aplicación
- **[docker-compose.yml](docker-compose.yml)** - Orquestación con Docker Compose

## ⚙️ Configuración

- **[.env.example](.env.example)** - Template de variables de entorno
- **[requirements-api.txt](requirements-api.txt)** - Dependencias de la API
- **[requirements.txt](requirements.txt)** - Dependencias completas (incluye training)

## 📁 Código Fuente

### Estructura por Capas (DDD)

```
src/
├── domain/          → Lógica de negocio pura (Entities, Value Objects)
├── application/     → Casos de uso (Use Cases, DTOs)
├── infrastructure/  → Implementaciones (ML services, Repositories, Config)
├── presentation/    → API REST (FastAPI endpoints, Schemas)
└── shared/          → Utilidades (Exceptions)
```

Ver [PROJECT-STRUCTURE.md](PROJECT-STRUCTURE.md) para detalles completos.

## 🔍 Buscar Información por Tema

### Quiero...

#### ...empezar rápidamente
→ [QUICKSTART.md](QUICKSTART.md)

#### ...entender la arquitectura
→ [ARCHITECTURE.md](ARCHITECTURE.md)

#### ...usar la API
→ [README-API.md](README-API.md) → sección "Uso de la API"

#### ...hacer predicciones con Python
→ [examples/api_usage.py](examples/api_usage.py)

#### ...desplegar en producción
→ [README-API.md](README-API.md) → sección "Docker"
→ [Dockerfile](Dockerfile) y [docker-compose.yml](docker-compose.yml)

#### ...modificar el código
→ [ARCHITECTURE.md](ARCHITECTURE.md) → Principios SOLID
→ [PROJECT-STRUCTURE.md](PROJECT-STRUCTURE.md) → Extensiones

#### ...agregar tests
→ [PROJECT-STRUCTURE.md](PROJECT-STRUCTURE.md) → Testing Strategy

#### ...configurar el entorno
→ [.env.example](.env.example)
→ [requirements-api.txt](requirements-api.txt)

#### ...ver la estructura completa
→ [PROJECT-STRUCTURE.md](PROJECT-STRUCTURE.md)

## 🎓 Conceptos Clave

### Domain-Driven Design (DDD)
- **Entities**: Objetos con identidad (ECGSignal, ArrhythmiaPrediction)
- **Value Objects**: Objetos inmutables sin identidad (RRInterval, SignalWindow)
- **Repositories**: Interfaces para persistencia
- **Use Cases**: Lógica de aplicación

### Clean Architecture
- **Independencia**: Capas externas dependen de internas, nunca al revés
- **Testability**: Fácil mockear dependencias
- **Flexibility**: Cambiar tecnologías sin afectar lógica de negocio

### Patrones Aplicados
- Repository Pattern
- Dependency Injection
- Factory Pattern
- DTO Pattern

## 📊 Endpoints de la API

Una vez iniciada la API (puerto 8000):

- **Documentación interactiva**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health
- **Predicción**: POST http://localhost:8000/api/v1/predictions/

## 🛠️ Stack Tecnológico

- **Framework**: FastAPI 0.109
- **ML**: TensorFlow 2.15, NumPy, SciPy
- **Validación**: Pydantic 2.5
- **Server**: Uvicorn
- **ECG Processing**: WFDB
- **Containerization**: Docker, Docker Compose

## 📝 Licencia

Ver [LICENSE](LICENSE)

## 🤝 Contribuir

1. Leer [ARCHITECTURE.md](ARCHITECTURE.md) para entender el diseño
2. Leer [PROJECT-STRUCTURE.md](PROJECT-STRUCTURE.md) para ubicar archivos
3. Seguir los principios DDD y Clean Architecture
4. Mantener la separación de capas
5. Escribir tests para nuevas features

## 📞 Soporte

- Documentación: Este directorio
- Issues: GitHub Issues
- API Docs: http://localhost:8000/docs (cuando esté corriendo)

---

**Última actualización**: Diciembre 2025
**Versión**: 1.0.0
