# Dockerfile optimizado para Hugging Face Spaces
FROM python:3.11-slim

# Configurar directorio de trabajo
WORKDIR /app

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY requirements-api.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements-api.txt

# Copiar código de la aplicación
COPY src/ ./src/
COPY models/ ./models/
COPY app_hf.py .
COPY .env.example .env

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 user && \
    chown -R user:user /app

USER user

# Exponer puerto (Hugging Face usa 7860)
EXPOSE 7860

# Comando de inicio
CMD ["uvicorn", "app_hf:app", "--host", "0.0.0.0", "--port", "7860"]
