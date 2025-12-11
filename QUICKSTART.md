# Quick Start Guide

## 🚀 Inicio Rápido

### Opción 1: Ejecución Local

```bash
# 1. Instalar dependencias
pip install -r requirements-api.txt

# 2. Configurar entorno
cp .env.example .env

# 3. Ejecutar servidor
python main.py
```

La API estará disponible en: http://localhost:8000

### Opción 2: Docker

```bash
# Build y run
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

### Opción 3: Docker sin compose

```bash
docker build -t ecg-api .
docker run -p 8000:8000 ecg-api
```

## 📊 Probar la API

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Documentación interactiva
Abrir en navegador: http://localhost:8000/docs

### 3. Ejemplo con Python
```bash
python examples/api_usage.py
```

## 🏗️ Estructura del Proyecto

```
├── src/
│   ├── domain/              # Entidades y lógica de negocio
│   ├── application/         # Casos de uso
│   ├── infrastructure/      # Implementaciones (ML, repos)
│   ├── presentation/        # API REST (FastAPI)
│   └── shared/              # Utilidades compartidas
├── models/                  # Modelos ML entrenados
├── examples/                # Ejemplos de uso
├── main.py                  # Punto de entrada
├── requirements-api.txt     # Dependencias
└── README-API.md           # Documentación completa
```

## 🔑 Endpoints Principales

- `GET /health` - Health check
- `POST /api/v1/predictions/` - Predecir arritmia
- `GET /docs` - Documentación Swagger
- `GET /redoc` - Documentación ReDoc

## 📚 Más Información

Ver `README-API.md` para documentación completa.
