# 🚀 Guía de Despliegue en Hugging Face Spaces

Esta guía te llevará paso a paso para desplegar tu API de detección de arritmias en Hugging Face Spaces de forma **GRATUITA y PERMANENTE**.

## 📋 Pre-requisitos

1. Cuenta en Hugging Face (gratis): https://huggingface.co/join
2. Git instalado en tu computadora
3. Tu proyecto funcionando localmente

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

Cuando hagas cambios en el código:

```powershell
# Hacer commit de los cambios
git add .
git commit -m "Descripción de los cambios"

# Push a Hugging Face
git push hf main
```

Hugging Face reconstruirá automáticamente tu Space.

## 🐛 Solución de Problemas

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
