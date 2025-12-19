"""
Script de verificación de instalación MLOps
Verifica que todas las dependencias y configuraciones estén correctas
"""
import sys
import importlib
from pathlib import Path

def check_import(module_name, package_name=None):
    """Verifica si un módulo puede ser importado"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name or module_name}")
        return True
    except ImportError:
        print(f"❌ {package_name or module_name} - NO INSTALADO")
        return False

def check_file_exists(filepath, description):
    """Verifica si un archivo existe"""
    path = Path(filepath)
    if path.exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - NO ENCONTRADO")
        return False

def check_directory_exists(dirpath, description):
    """Verifica si un directorio existe"""
    path = Path(dirpath)
    if path.exists() and path.is_dir():
        print(f"✅ {description}: {dirpath}")
        return True
    else:
        print(f"⚠️  {description}: {dirpath} - NO ENCONTRADO (se creará automáticamente)")
        return True  # No es crítico

def main():
    print("="*80)
    print("🔍 VERIFICACIÓN DE INSTALACIÓN MLOps")
    print("="*80)
    print()
    
    all_ok = True
    
    # 1. Dependencias Python
    print("📦 Dependencias Python:")
    print("-"*80)
    dependencies = [
        ("mlflow", "MLflow"),
        ("evidently", "Evidently AI"),
        ("optuna", "Optuna"),
        ("tensorflow", "TensorFlow"),
        ("numpy", "NumPy"),
        ("pandas", "Pandas"),
        ("sklearn", "scikit-learn"),
        ("imblearn", "imbalanced-learn"),
        ("wfdb", "WFDB"),
        ("matplotlib", "Matplotlib")
    ]
    
    for module, name in dependencies:
        if not check_import(module, name):
            all_ok = False
    
    print()
    
    # 2. Archivos de configuración
    print("📄 Archivos de configuración MLOps:")
    print("-"*80)
    files = [
        ("mlflow_config.py", "Configuración MLflow"),
        ("start_mlflow.ps1", "Script inicio MLflow UI"),
        ("monitoring/drift_detector.py", "Detector de Drift"),
        ("optimize_hyperparameters.py", "Optimizador Optuna"),
        ("compare_models.py", "Comparador de modelos"),
        (".github/workflows/mlops-train.yml", "Workflow CI/CD entrenamiento"),
        (".github/workflows/monitoring.yml", "Workflow monitoreo"),
        ("MLOPS_GUIDE.md", "Guía MLOps"),
        ("MLOPS_QUICKSTART.md", "Quick Start MLOps")
    ]
    
    for filepath, desc in files:
        if not check_file_exists(filepath, desc):
            all_ok = False
    
    print()
    
    # 3. Directorios
    print("📁 Directorios del proyecto:")
    print("-"*80)
    directories = [
        ("models/ecg_nv_cnn", "Modelos entrenados"),
        ("monitoring", "Scripts de monitoreo"),
        (".github/workflows", "GitHub Actions workflows")
    ]
    
    for dirpath, desc in directories:
        check_directory_exists(dirpath, desc)
    
    print()
    
    # 4. Verificar MLflow
    print("🔧 Configuración MLflow:")
    print("-"*80)
    try:
        import mlflow
        mlflow.set_tracking_uri("file:./mlruns")
        
        # Intentar listar experimentos
        experiments = mlflow.search_experiments()
        print(f"✅ MLflow tracking URI configurado")
        print(f"   Experimentos encontrados: {len(experiments)}")
        
        # Buscar experimento específico
        exp = mlflow.get_experiment_by_name("deteccion_arritmias_ecg")
        if exp:
            print(f"✅ Experimento 'deteccion_arritmias_ecg' encontrado")
            runs = mlflow.search_runs(experiment_ids=[exp.experiment_id])
            print(f"   Runs registrados: {len(runs)}")
        else:
            print(f"⚠️  Experimento 'deteccion_arritmias_ecg' no existe aún")
            print(f"   (se creará al ejecutar deteccionarritmias.py)")
    except Exception as e:
        print(f"❌ Error configurando MLflow: {e}")
        all_ok = False
    
    print()
    
    # 5. Resumen
    print("="*80)
    if all_ok:
        print("✅ VERIFICACIÓN COMPLETADA EXITOSAMENTE")
        print()
        print("🚀 Próximos pasos:")
        print("   1. Entrenar modelo: python deteccionarritmias.py")
        print("   2. Ver experimentos: .\\start_mlflow.ps1")
        print("   3. Comparar modelos: python compare_models.py")
        print()
        print("📚 Lee MLOPS_QUICKSTART.md para empezar")
    else:
        print("⚠️  VERIFICACIÓN COMPLETADA CON ADVERTENCIAS")
        print()
        print("🔧 Solución:")
        print("   pip install -r requirements-api.txt")
        print()
        print("Si persisten los errores, consulta MLOPS_GUIDE.md")
    
    print("="*80)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
