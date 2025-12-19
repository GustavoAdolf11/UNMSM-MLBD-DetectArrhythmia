# 🚀 Guía de Despliegue en Hugging Face Spaces (con MLOps)

Esta guía te llevará paso a paso para desplegar tu API de detección de arritmias en Hugging Face Spaces de forma **GRATUITA y PERMANENTE**, integrando MLflow para desplegar automáticamente el mejor modelo entrenado.

## 📋 Pre-requisitos

1. ✅ Cuenta en Hugging Face (gratis): https://huggingface.co/join
2. ✅ Git instalado en tu computadora
3. ✅ Tu proyecto funcionando localmente
4. ✅ **MLflow configurado** con al menos un experimento (ver [MLOPS_QUICKSTART.md](MLOPS_QUICKSTART.md))
5. ✅ **Al menos un modelo entrenado** registrado en MLflow

## 🎯 Paso 0: Entrenar y Seleccionar Mejor Modelo (NUEVO)

Antes de desplegar, asegúrate de tener modelos entrenados en MLflow.

### 0.1 Entrenar modelos

```powershell
# Entrenar modelo base
python deteccionarritmias.py

# O entrenar múltiples modelos con optimización (opcional)
python optimize_hyperparameters.py --n-trials 10
```

### 0.2 Verificar experimentos en MLflow

```powershell
# Abrir MLflow UI
.\start_mlflow.ps1

# En el navegador (http://localhost:5000):
# - Ver todos los experimentos
# - Comparar métricas (F1-Score V, Accuracy)
# - El script de despliegue seleccionará el mejor automáticamente
```

---

## 🎯 Paso 1: Crear un Space en Hugging Face

1. Ve a https://huggingface.co/spaces
2. Haz clic en **"Create new Space"**
3. Configura tu Space:
   - **Space name**: `ecg-arrhythmia-detection` (o el nombre que prefieras)
   - **License**: MIT
   - **Select the Space SDK**: **Docker** ⚠️ MUY IMPORTANTE
   - **Space hardware**: CPU basic (gratis)
   - **Visibility**: Public (o Private si prefieres)
4. Haz clic en **"Create Space"**

## 🔧 Paso 2: Preparar el Repositorio Local

### 2.1 Inicializar Git (si no lo has hecho)

```powershell
# En el directorio del proyecto
git init
git add .
git commit -m "Initial commit: ECG Arrhythmia Detection API"
```

### 2.2 Renombrar archivos para Hugging Face

```powershell
# Copiar README especial para Hugging Face
Copy-Item README_HF.md README.md -Force

# Copiar Dockerfile especial para Hugging Face
Copy-Item Dockerfile.hf Dockerfile -Force
```

## 🌐 Paso 3: Conectar con Hugging Face

### 3.1 Obtener tu token de acceso

1. Ve a https://huggingface.co/settings/tokens
2. Haz clic en **"New token"**
3. Nombre: `deploy-ecg-api`
4. Role: **Write**
5. Copia el token generado

### 3.2 Configurar Git remote

```powershell
# Reemplaza YOUR_USERNAME y YOUR_SPACE_NAME con tus valores
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME

# Ejemplo:
# git remote add hf https://huggingface.co/spaces/GustavoAdolf11/ecg-arrhythmia-detection
```

### 3.3 Configurar credenciales

```powershell
# Cuando hagas push, Git te pedirá:
# Username: tu_username_de_huggingface
# Password: tu_token_de_acceso (el que copiaste)
```

## 📤 Paso 4: Desplegar

```powershell
# Hacer push al Space
git push hf main

# Si tu rama se llama 'master' en lugar de 'main':
git push hf master:main
```

## ⏳ Paso 5: Esperar el Build

1. Ve a tu Space en Hugging Face: `https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME`
2. Verás el proceso de build en tiempo real (tarda 5-10 minutos la primera vez)
3. Estados:
   - 🟡 **Building**: Construyendo la imagen Docker
   - 🟢 **Running**: ¡Tu API está en línea!
   - 🔴 **Error**: Revisa los logs para ver qué falló

## ✅ Paso 6: Probar tu API

### 6.1 Acceder a la documentación

```
https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/docs
```

Ejemplo: `https://gustavoadolf11-ecg-arrhythmia-detection.hf.space/docs`

### 6.2 Probar el endpoint de salud

```bash
curl https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/health
```

### 6.3 Hacer una predicción

```bash
curl -X POST "https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/api/v1/predictions/" \
  -H "Content-Type: application/json" \
  -d @test_payload_10s.json
```

## 🔄 Actualizar tu API

### Opción 1: Despliegue MLOps Automático (RECOMENDADO)

Cuando entrenes nuevos modelos, despliega automáticamente el mejor:

```powershell
# 1. Entrenar nuevo modelo
python deteccionarritmias.py

# 2. El script selecciona automáticamente el mejor modelo de MLflow y despliega
.\deploy-to-hf-mlops.ps1
```

Este script:
- ✅ Busca el mejor modelo por F1-Score de clase V en MLflow
- ✅ Lo copia al directorio de producción
- ✅ Crea commit con métricas del modelo
- ✅ Despliega automáticamente a Hugging Face

### Opción 2: Despliegue Manual

Cuando hagas cambios en el código (sin cambiar modelo):

```powershell
# Hacer commit de los cambios
git add .
git commit -m "Descripción de los cambios"

# Push a Hugging Face
git push hf main
```

Hugging Face reconstruirá automáticamente tu Space.

---

## 📊 Trazabilidad de Modelos en Producción

Cada despliegue con MLOps registra:
- **Run ID de MLflow** en el historial de Git
- **Métricas del modelo** (F1-Score V, Accuracy, Precision, Recall)
- **Timestamp** del entrenamiento
- **Hiperparámetros** usados

### Ver historial de despliegues

```powershell
# Ver commits de despliegues
git log --oneline --grep="Deploy: MLflow"

# Ejemplo de salida:
# abc123 Deploy: MLflow model (F1-V: 0.8542, Acc: 0.9234)
# def456 Deploy: MLflow model (F1-V: 0.8301, Acc: 0.9156)
```

---

## 🐛 Solución de Problemas

### ❌ Error: "No hay experimentos registrados"

**Causa:** No has entrenado ningún modelo con MLflow.

**Solución:**
```powershell
# Entrenar modelo
python deteccionarritmias.py

# Verificar que se creó el experimento
.\start_mlflow.ps1
# Abre http://localhost:5000 y verifica que aparece "deteccion_arritmias_ecg"
```

### ❌ Error: "Modelo no encontrado"

**Causa:** El artifact del modelo no se guardó en MLflow.

**Solución:**
```powershell
# Verificar estructura de MLflow
ls mlruns/

# Buscar modelos guardados
ls mlruns/*/*/artifacts/models/

# Si no hay modelos, reentrenar
python deteccionarritmias.py
```

### ❌ Error: "Remoto 'hf' no configurado"

**Causa:** No has conectado tu repositorio con Hugging Face.

**Solución:**
```powershell
# Configurar remoto (sustituye con tu URL real)
git remote add hf https://huggingface.co/spaces/TU_USUARIO/TU_SPACE

# Verificar
git remote -v
```

### Error: "Git LFS required"

Si tu modelo es muy grande (>10MB):

```powershell
# Instalar Git LFS
# Windows: Descarga desde https://git-lfs.github.com/

# Configurar Git LFS
git lfs install

# Rastrear archivos grandes
git lfs track "models/**/*.keras"
git lfs track "*.h5"

# Commit y push
git add .gitattributes
git commit -m "Add Git LFS"
git push hf main
```

### ❌ Hugging Face rechaza el push (modelo muy grande)

**Solución:**
```powershell
# Usar Git LFS para archivos >10MB
git lfs install
git lfs track "*.keras"
git lfs track "*.h5"
git add .gitattributes
git commit -m "Configure Git LFS"
git push hf main
```

### ⚠️ Build falla en Hugging Face

**Solución:**
1. Ve a tu Space en HF y revisa los logs del build
2. Verifica que `Dockerfile.hf` existe y está correcto
3. Asegúrate de que `requirements-api.txt` tiene todas las dependencias

---

## 💡 Mejores Prácticas

1. **Siempre entrenar primero** antes de desplegar
   ```powershell
   python deteccionarritmias.py
   .\deploy-to-hf-mlops.ps1
   ```

2. **Comparar métricas** en MLflow UI antes de desplegar
   ```powershell
   .\start_mlflow.ps1
   # Revisar que el nuevo modelo realmente mejoró
   ```

3. **Mantener historial** de modelos en MLflow (no eliminar runs antiguos)
   - Permite rollback si el nuevo modelo falla
   - Comparar evolución del modelo

4. **Documentar cambios significativos** en commits
   ```powershell
   git commit -m "feat: Improved preprocessing with new bandpass filter"
   ```

5. **Monitorear después del despliegue**
   - Verificar que la API responde en HF Space
   - Probar endpoint `/docs` y `/health`
   - Hacer predicción de prueba

---

## 🎯 Próximos Pasos

Después de desplegar exitosamente:

1. **[Configurar monitoreo](MLOPS_GUIDE.md#monitoreo-y-drift-detection)** - Detectar degradación del modelo
2. **[CI/CD automático](.github/workflows/mlops-train.yml)** - Re-entrenamiento programado
3. **[A/B Testing](MLOPS_GUIDE.md#despliegue-de-modelos)** - Comparar modelos en producción
4. **Integrar con aplicaciones** - Frontend, apps móviles, etc.

---

## 📞 Recursos

- **Documentación MLOps:** [MLOPS_GUIDE.md](MLOPS_GUIDE.md)
- **Inicio rápido MLOps:** [MLOPS_QUICKSTART.md](MLOPS_QUICKSTART.md)
- **Hugging Face Docs:** https://huggingface.co/docs/hub/spaces
- **MLflow Docs:** https://mlflow.org/docs/latest/index.html

---

**¡Listo!** Tu modelo está desplegado con trazabilidad completa MLOps. 🚀

### Error: "Build failed"

1. Revisa los logs en la pestaña "Logs" de tu Space
2. Verifica que `Dockerfile.hf` y `requirements-api.txt` estén correctos
3. Asegúrate de que el modelo esté en `models/ecg_nv_cnn/model_v7.keras`

### Error: "Port 7860 not exposed"

Verifica que `Dockerfile.hf` tenga:
```dockerfile
EXPOSE 7860
CMD ["uvicorn", "app_hf:app", "--host", "0.0.0.0", "--port", "7860"]
```

### El Space se queda "Building" por mucho tiempo

- Es normal la primera vez (5-15 minutos)
- Si pasa de 20 minutos, revisa los logs
- Puede ser por descargar TensorFlow y otras dependencias pesadas

## 📊 Monitoreo

### Ver logs en tiempo real

1. Ve a tu Space en Hugging Face
2. Pestaña **"Logs"**
3. Verás todos los logs de tu aplicación

### Estadísticas de uso

Hugging Face te mostrará:
- Número de usuarios
- Requests por día
- Tiempo de respuesta promedio

## 🎉 ¡Listo!

Tu API ahora está:
- ✅ Desplegada en la nube
- ✅ Accesible 24/7
- ✅ Completamente GRATIS
- ✅ Sin límite de tiempo
- ✅ Con HTTPS automático
- ✅ Con documentación Swagger

## 🔗 URLs Importantes

- **Tu Space**: `https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME`
- **Tu API**: `https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space`
- **Swagger Docs**: `https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/docs`
- **Redoc**: `https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/redoc`

## 💡 Consejos

1. **Mantén el README.md actualizado** - Es la cara visible de tu Space
2. **Usa Git LFS para archivos grandes** - Modelos, datasets, etc.
3. **Monitorea los logs** - Para detectar errores rápido
4. **Versiona tus cambios** - Usa commits descriptivos
5. **Prueba localmente primero** - Antes de hacer push

## 📞 Soporte

- Documentación oficial: https://huggingface.co/docs/hub/spaces
- Discord de Hugging Face: https://discord.gg/hugging-face
- Foro: https://discuss.huggingface.co/

---

**¿Problemas?** Revisa los logs de tu Space o contacta al equipo de soporte de Hugging Face.
