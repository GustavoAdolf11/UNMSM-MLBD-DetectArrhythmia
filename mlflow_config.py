"""
Configuración centralizada para MLflow
"""
import os
from pathlib import Path

# Rutas del proyecto
PROJECT_ROOT = Path(__file__).parent
MLRUNS_DIR = PROJECT_ROOT / "mlruns"
MODELS_DIR = PROJECT_ROOT / "models"

# Configuración de MLflow
MLFLOW_TRACKING_URI = f"file:{MLRUNS_DIR.as_posix()}"
EXPERIMENT_NAME = "deteccion_arritmias_ecg"

# Configuración de modelos registrados
REGISTERED_MODEL_NAME = "ECG_Arritmias_NvsV"

# Tags por defecto para runs
DEFAULT_TAGS = {
    "project": "deteccion-arritmias",
    "framework": "tensorflow/keras",
    "dataset": "MIT-BIH"
}

def get_mlflow_config():
    """Retorna configuración completa de MLflow"""
    return {
        "tracking_uri": MLFLOW_TRACKING_URI,
        "experiment_name": EXPERIMENT_NAME,
        "registered_model_name": REGISTERED_MODEL_NAME,
        "default_tags": DEFAULT_TAGS
    }

def setup_mlflow():
    """Configura MLflow con las opciones del proyecto"""
    import mlflow
    
    # Crear directorio mlruns si no existe
    MLRUNS_DIR.mkdir(exist_ok=True)
    
    # Configurar tracking URI
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    
    # Configurar experimento
    mlflow.set_experiment(EXPERIMENT_NAME)
    
    print(f"✅ MLflow configurado")
    print(f"   Tracking URI: {MLFLOW_TRACKING_URI}")
    print(f"   Experimento: {EXPERIMENT_NAME}")
    
    return mlflow.get_experiment_by_name(EXPERIMENT_NAME)

if __name__ == "__main__":
    setup_mlflow()
    print("\n📊 Para ver el UI de MLflow, ejecuta:")
    print("   mlflow ui")
    print("   Luego abre: http://127.0.0.1:5000")
