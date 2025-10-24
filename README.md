# Detector de Arritmias Cardíacas con Deep Learning

Sistema de detección automática de arritmias ventriculares en señales ECG usando redes neuronales convolucionales (CNN).

## Descripción

Este proyecto implementa un clasificador binario para detectar arritmias ventriculares (clase V) vs latidos normales (clase N) en señales ECG usando una arquitectura CNN-1D con características RR. El modelo alcanza:

- Accuracy: 87.63%
- Sensibilidad para arritmias (V): 95.58%
- Precisión para latidos normales (N): 99.41%

## Requisitos

- Python 3.8+
- CUDA compatible GPU (opcional, recomendado para entrenamiento)
- Dependencias en `requirements.txt`

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/GustavoAdolf11/UNMSM-MLBD-DetectArrhythmia.git
cd UNMSM-MLBD-DetectArrhythmia
```

2. Crear entorno virtual:
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Datos

El proyecto usa la base de datos MIT-BIH Arrhythmia. Para descargar:

1. Visitar [PhysioNet MIT-BIH Arrhythmia Database](https://physionet.org/content/mitdb/1.0.0/)
2. Descargar archivos .dat, .hea y .atr
3. Colocar en carpeta `mit-bih/`

## Uso

```bash
python deteccionarritmias.py
```

El script entrenará el modelo y guardará:
- Modelo en formato .keras
- Modelo en TFLite
- Métricas y gráficas de evaluación

## Licencia

Este proyecto está bajo la Licencia MIT - ver archivo [LICENSE](LICENSE) para detalles.