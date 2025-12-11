# 📚 Ejemplos de Uso - API de Detección de Arritmias

Esta carpeta contiene ejemplos prácticos para probar y usar la API de detección de arritmias.

## 📁 Contenido

### 🧪 Datos de Prueba

- **`test_payload_10s.json`** - Señal ECG sintética de 10 segundos (3600 muestras)
  - Duración: 10 segundos (mínimo requerido)
  - Frecuencia: 360 Hz
  - Uso: Pruebas básicas y validación de la API

- **`test_payload_30s.json`** - Señal ECG sintética de 30 segundos (10800 muestras)
  - Duración: 30 segundos
  - Frecuencia: 360 Hz  
  - Uso: Pruebas más robustas con más latidos

### 🔧 Scripts de Utilidad

- **`generate_test_data.py`** - Generador de datos de prueba sintéticos
  - Crea señales ECG con morfología realista (P, QRS, T)
  - Frecuencia cardíaca: 75 bpm
  - Genera archivos JSON listos para usar

- **`api_usage.py`** - Cliente Python de ejemplo
  - Muestra cómo consumir la API desde Python
  - Incluye manejo de errores
  - Parseo de respuestas

- **`curl_examples.sh`** - Ejemplos con curl
  - Comandos listos para copiar y pegar
  - Pruebas con curl desde terminal

## 🚀 Cómo Probar la API

### 1. Probar API Local

#### Con Python:

```python
import requests
import json

# Cargar datos de prueba
with open('examples/test_payload_10s.json', 'r') as f:
    payload = json.load(f)

# Hacer request
response = requests.post(
    'http://localhost:8000/api/v1/predictions/',
    json=payload
)

# Ver resultados
if response.status_code == 200:
    result = response.json()
    print(f"Tipo de arritmia: {result['overall_arrhythmia_type']}")
    print(f"Confianza: {result['confidence']:.2%}")
    print(f"Nivel de riesgo: {result['risk_level']}")
    print(f"Latidos detectados: {result['total_beats_detected']}")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

#### Con curl (PowerShell):

```powershell
# Health check
curl http://localhost:8000/health

# Predicción
curl -X POST "http://localhost:8000/api/v1/predictions/" `
  -H "Content-Type: application/json" `
  -d "@examples/test_payload_10s.json"
```

#### Con Swagger UI:

1. Abre http://localhost:8000/docs
2. Expande POST `/api/v1/predictions/`
3. Click en "Try it out"
4. Copia el contenido de `test_payload_10s.json`
5. Pega en el campo Request body
6. Click en "Execute"

### 2. Probar API Desplegada en Hugging Face

```python
import requests
import json

# URL de tu Space en Hugging Face
API_URL = "https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/api/v1/predictions/"

with open('examples/test_payload_10s.json', 'r') as f:
    payload = json.load(f)

response = requests.post(API_URL, json=payload)
result = response.json()
print(result)
```

#### Con curl:

```powershell
curl -X POST "https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/api/v1/predictions/" `
  -H "Content-Type: application/json" `
  -d "@examples/test_payload_10s.json"
```

## 📊 Formato de la Solicitud

```json
{
  "signal_data": [0.1, 0.15, 0.2, ...],  // Mínimo 3600 valores (10 segundos)
  "sampling_rate": 360,                   // Frecuencia de muestreo en Hz
  "derivation": "MLII",                   // Derivación ECG (MLII, V5, etc.)
  "patient_id": "TEST001",                // ID del paciente (opcional)
  "apply_ruleguard": true                 // Aplicar filtro de falsos positivos
}
```

### Requisitos:

- ✅ `signal_data`: Mínimo 3600 muestras (10 segundos a 360 Hz)
- ✅ `sampling_rate`: Entre 100-1000 Hz (recomendado: 360 Hz)
- ✅ `derivation`: Cualquier string (por defecto: "MLII")
- ✅ `apply_ruleguard`: `true` recomendado para reducir falsos positivos

## 📋 Formato de la Respuesta

```json
{
  "prediction_id": "uuid-generado",
  "timestamp": "2025-12-10T12:00:00.000Z",
  "patient_id": "TEST001",
  "overall_arrhythmia_type": "N",        // "N" = Normal, "V" = Ventricular
  "confidence": 0.95,                     // Confianza promedio [0-1]
  "risk_level": "LOW",                    // LOW, MEDIUM, HIGH
  "total_beats_detected": 12,
  "beat_predictions": [
    {
      "beat_index": 0,
      "position_sample": 180,
      "arrhythmia_type": "N",
      "confidence": 0.96,
      "rr_previous": 0.833
    },
    // ... más latidos
  ]
}
```

## 🔬 Generar Nuevos Datos de Prueba

Si necesitas datos de prueba personalizados:

```powershell
# Activar entorno virtual
.\detectArritmia\Scripts\Activate.ps1

# Generar datos
python examples/generate_test_data.py
```

Esto creará:
- `test_payload_10s.json` (10 segundos)
- `test_payload_30s.json` (30 segundos)

## 🏥 Usar Datos Reales MIT-BIH

Para probar con datos reales de la base de datos MIT-BIH:

```python
import wfdb
import json

# Leer registro MIT-BIH (ej: registro 100)
record = wfdb.rdrecord('mit-bih/100')
signal_data = record.p_signal[:3600, 0].tolist()  # 10 segundos, canal 0

payload = {
    "signal_data": signal_data,
    "sampling_rate": 360,
    "derivation": "MLII",
    "patient_id": "MIT-BIH-100",
    "apply_ruleguard": True
}

# Guardar o enviar directamente
with open('test_mit_bih_100.json', 'w') as f:
    json.dump(payload, f)
```

## ❌ Errores Comunes

### Error: "ECG signal too short"
**Causa**: Menos de 3600 muestras (10 segundos a 360 Hz)  
**Solución**: Usa `test_payload_10s.json` o aumenta la duración de tu señal

### Error: 422 "List should have at least 360 items"
**Causa**: Array `signal_data` muy corto  
**Solución**: Verifica que tengas al menos 360 valores en el array

### Error: "JSON decode error"
**Causa**: JSON mal formateado  
**Solución**: Valida tu JSON en jsonlint.com o usa los archivos de ejemplo

### Error: "No R peaks detected"
**Causa**: Señal sin morfología ECG reconocible  
**Solución**: Usa datos de prueba sintéticos o reales del MIT-BIH

## 📞 Soporte

- **Documentación API**: http://localhost:8000/docs (local) o https://YOUR-SPACE.hf.space/docs
- **Repositorio**: https://github.com/GustavoAdolf11/UNMSM-MLBD-DetectArrhythmia
- **Issues**: Reporta problemas en GitHub Issues

## 📄 Licencia

MIT License - Ver archivo LICENSE en la raíz del proyecto
