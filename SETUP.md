# ⚙️ Setup del Proyecto - Entorno Virtual

Este proyecto utiliza un **entorno virtual** para aislar las dependencias.

## 📦 Instalación Completa (Paso a Paso)

### 1️⃣ Clonar Repositorio

```powershell
git clone <URL-del-repositorio>
cd "proyectoML - copia - copia"
```

### 2️⃣ Crear Entorno Virtual

```powershell
python -m venv venv
```

Esto crea una carpeta `venv/` con Python aislado.

### 3️⃣ Activar Entorno Virtual

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Si da error de permisos:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Verificar activación:**
Deberías ver `(venv)` al inicio de tu terminal:
```
(venv) PS E:\proyectoML>
```

### 4️⃣ Actualizar pip

```powershell
python -m pip install --upgrade pip
```

### 5️⃣ Instalar Dependencias

```powershell
pip install -r requirements-api.txt
```

**Esto instala:**
- TensorFlow 2.20.0
- MLflow 3.7.0
- Scikit-learn 1.8.0
- Pandas, NumPy, SciPy
- Evidently (drift detection)
- Optuna (hyperparameter tuning)
- FastAPI, Uvicorn
- Y más...

### 6️⃣ Verificar Instalación

```powershell
python verify_mlops_setup.py
```

Deberías ver:
```
✅ VERIFICACIÓN COMPLETADA EXITOSAMENTE
```

---

## 🚀 Uso Diario

### Activar Entorno (cada sesión)

**IMPORTANTE:** Cada vez que abras una nueva terminal, debes activar el entorno:

```powershell
.\venv\Scripts\Activate.ps1
```

### Entrenar Modelo

```powershell
python deteccionarritmias.py
```

### Ver Experimentos MLflow

```powershell
.\start_mlflow.ps1
```

### Desactivar Entorno (al terminar)

```powershell
deactivate
```

---

## 🔄 Reproducibilidad

### Para otros desarrolladores

**Archivo `requirements-api.txt`:**
Contiene TODAS las dependencias con versiones exactas.

**Pasos para replicar:**
```powershell
# 1. Clonar repo
git clone <URL>

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar
.\venv\Scripts\Activate.ps1

# 4. Instalar dependencias
pip install -r requirements-api.txt

# 5. Listo!
python deteccionarritmias.py
```

### Actualizar dependencias

Si instalas algo nuevo:

```powershell
# Instalar
pip install nueva-libreria

# Actualizar requirements
pip freeze > requirements-api.txt
```

---

## 🐛 Troubleshooting

### ❌ Error: "cannot import name '_is_pandas_df'"

**Solución:**
```powershell
pip install --upgrade scikit-learn imbalanced-learn
```

### ❌ PowerShell no permite ejecutar scripts

**Solución:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### ❌ Módulo no encontrado

**Causa:** Entorno virtual NO activado.

**Solución:**
```powershell
.\venv\Scripts\Activate.ps1
```

Verifica que aparezca `(venv)` en la terminal.

### ❌ Conflictos de versiones

**Solución:** Eliminar y recrear entorno:
```powershell
deactivate
Remove-Item -Recurse -Force venv
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements-api.txt
```

---

## 📋 Comandos Útiles

```powershell
# Ver paquetes instalados
pip list

# Ver dependencias de un paquete
pip show mlflow

# Verificar versión de Python
python --version

# Ver ubicación de Python (debe ser dentro de venv/)
where python
# Debe mostrar: E:\proyectoML - copia - copia\venv\Scripts\python.exe
```

---

## ✅ Checklist de Instalación

- [ ] Python 3.10+ instalado
- [ ] Entorno virtual creado (`venv/`)
- [ ] Entorno virtual activado (`(venv)` visible)
- [ ] `pip` actualizado
- [ ] Dependencias instaladas (`requirements-api.txt`)
- [ ] Verificación pasada (`verify_mlops_setup.py`)
- [ ] Primer entrenamiento exitoso

---

## 🎯 Siguiente Paso

Una vez completada la instalación, lee:
- [MLOPS_QUICKSTART.md](MLOPS_QUICKSTART.md) - Uso básico de MLOps
- [MLOPS_GUIDE.md](MLOPS_GUIDE.md) - Guía completa
