# 🚀 Guía de Despliegue - ECG Arrhythmia API

## Opción 1: Render.com (Recomendado - GRATIS)

### Paso 1: Preparar el Repositorio
```bash
git add .
git commit -m "Preparar para despliegue en Render"
git push origin master
```

### Paso 2: Crear Cuenta en Render
1. Ve a https://render.com
2. "Sign Up" con GitHub
3. Autoriza Render a acceder a tus repositorios

### Paso 3: Crear Web Service
1. Click en "New +" → "Web Service"
2. Conecta tu repositorio: `GustavoAdolf11/UNMSM-MLBD-DetectArrhythmia`
3. Configura:
   - **Name**: `ecg-arrhythmia-api` (o el que quieras)
   - **Region**: `Oregon (US West)` (o el más cercano)
   - **Branch**: `master`
   - **Root Directory**: `.` (dejar vacío)
   - **Runtime**: `Python 3`
   - **Build Command**: 
     ```
     pip install --upgrade pip && pip install -r requirements-api.txt
     ```
   - **Start Command**: 
     ```
     uvicorn src.presentation.app:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type**: `Free`

### Paso 4: Variables de Entorno (Opcional)
En "Environment Variables" agrega:
```
DEBUG=False
MODEL_THRESHOLD=0.5
USE_RULEGUARD=True
```

### Paso 5: Deploy
1. Click "Create Web Service"
2. Espera 5-10 minutos (primera vez)
3. ¡Listo! Tu API estará en: `https://ecg-arrhythmia-api.onrender.com`

### Paso 6: Probar
```bash
curl https://ecg-arrhythmia-api.onrender.com/health
```

O abre en navegador:
```
https://ecg-arrhythmia-api.onrender.com/docs
```

---

## Opción 2: Railway.app (Más rápido, $5 gratis/mes)

### Paso 1: Subir a GitHub (igual que antes)

### Paso 2: Crear cuenta en Railway
1. https://railway.app
2. "Start a New Project"
3. "Deploy from GitHub repo"

### Paso 3: Configurar
Railway detecta Python automáticamente.

Si necesitas ajustar:
- **Build Command**: `pip install -r requirements-api.txt`
- **Start Command**: `uvicorn src.presentation.app:app --host 0.0.0.0 --port $PORT`

### Paso 4: Deploy
Railway despliega automáticamente. ¡Listo!

---

## Opción 3: Hugging Face Spaces

### Paso 1: Crear Space
1. https://huggingface.co/spaces
2. "Create new Space"
3. Tipo: "Docker"
4. Nombre: `ecg-arrhythmia-api`

### Paso 2: Subir archivos
Sube tu código al Space (vía web o git)

### Paso 3: Crear `Dockerfile` para HF
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-api.txt .
RUN pip install -r requirements-api.txt

COPY . .

EXPOSE 7860

CMD ["uvicorn", "src.presentation.app:app", "--host", "0.0.0.0", "--port", "7860"]
```

---

## Opción 4: Google Cloud Run (Serverless, Pago por uso)

### Requisitos
- Cuenta de Google Cloud (300$ gratis)
- gcloud CLI instalado

### Paso 1: Build Docker
```bash
gcloud builds submit --tag gcr.io/TU-PROJECT-ID/ecg-api
```

### Paso 2: Deploy
```bash
gcloud run deploy ecg-api \
  --image gcr.io/TU-PROJECT-ID/ecg-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000
```

---

## Opción 5: Heroku (Fácil pero de pago desde 2022)

Ya no tiene plan gratuito, pero es muy sencillo:

```bash
heroku create ecg-arrhythmia-api
git push heroku master
```

---

## 📊 Comparación

| Plataforma | Precio | Facilidad | Rendimiento | Recomendado para |
|------------|--------|-----------|-------------|------------------|
| **Render** | Gratis | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Demos, MVPs |
| **Railway** | $5/mes | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Producción pequeña |
| **HF Spaces** | Gratis | ⭐⭐⭐⭐ | ⭐⭐ | Demos ML |
| **GCP Run** | Pay-as-go | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Producción escalable |
| **AWS/Azure** | $$$ | ⭐⭐ | ⭐⭐⭐⭐⭐ | Enterprise |

---

## 🔧 Troubleshooting

### Error: Modelo no se carga
- **Problema**: El modelo es muy pesado (>512MB en Render free)
- **Solución 1**: Subir modelo a GitHub LFS
- **Solución 2**: Guardar modelo en servicio externo (S3, Google Drive)
- **Solución 3**: Usar Railway ($5/mes, más memoria)

### Error: Out of memory
- Render free tiene 512MB RAM
- TensorFlow puede usar más
- **Solución**: Usar Railway o GCP

### API lenta en primera request (Render)
- Normal, el servicio se "duerme" después de 15 min
- Primera request tarda ~30 segundos
- **Solución**: Upgrade a plan pagado ($7/mes) o usar Railway

---

## 🎯 Mi Recomendación

**Para empezar**: **Render.com** (gratis, fácil)

**Para producción**: **Railway.app** ($5/mes, mejor rendimiento)

**Para escalar**: **Google Cloud Run** (pago por uso, escalable)

---

## 📝 Próximos Pasos

1. Sube tu código a GitHub
2. Crea cuenta en Render.com
3. Conecta tu repo
4. Deploy en 5 minutos
5. Comparte tu API: `https://tu-app.onrender.com/docs`

¿Necesitas ayuda con algún paso específico?
