"""
Ejemplo de uso de MLflow - Demostracion práctica
Muestra cómo trabajar con MLflow después de entrenar modelos
"""
import mlflow
import pandas as pd
from mlflow_config import setup_mlflow

def ejemplo_1_listar_experimentos():
    """Ejemplo 1: Listar todos los experimentos"""
    print("\n" + "="*80)
    print("EJEMPLO 1: Listar Experimentos")
    print("="*80)
    
    experiments = mlflow.search_experiments()
    
    print(f"\nTotal de experimentos: {len(experiments)}\n")
    
    for exp in experiments:
        print(f"📊 {exp.name}")
        print(f"   Experiment ID: {exp.experiment_id}")
        print(f"   Ubicación: {exp.artifact_location}")
        print()

def ejemplo_2_buscar_mejores_modelos():
    """Ejemplo 2: Buscar los mejores modelos por F1 Score"""
    print("\n" + "="*80)
    print("EJEMPLO 2: Top 5 Modelos (por F1 Score)")
    print("="*80)
    
    # Buscar el experimento
    exp = mlflow.get_experiment_by_name("deteccion_arritmias_ecg")
    
    if not exp:
        print("⚠️  Experimento 'deteccion_arritmias_ecg' no existe aún")
        print("   Ejecuta primero: python deteccionarritmias.py")
        return
    
    # Buscar runs ordenados por F1
    runs = mlflow.search_runs(
        experiment_ids=[exp.experiment_id],
        order_by=["metrics.test_f1_V DESC"],
        max_results=5
    )
    
    if runs.empty:
        print("⚠️  No hay runs registrados aún")
        return
    
    print("\n🏆 Top 5 Modelos:\n")
    
    # Seleccionar columnas relevantes
    cols = [
        'run_id',
        'start_time',
        'metrics.test_f1_V',
        'metrics.test_accuracy',
        'metrics.test_precision_V',
        'metrics.test_recall_V'
    ]
    
    available_cols = [c for c in cols if c in runs.columns]
    
    for idx, row in runs[available_cols].head().iterrows():
        print(f"{idx+1}. Run ID: {row['run_id'][:8]}...")
        if 'start_time' in row:
            print(f"   Fecha: {row['start_time']}")
        if 'metrics.test_f1_V' in row:
            print(f"   F1 Score: {row['metrics.test_f1_V']:.4f}")
        if 'metrics.test_accuracy' in row:
            print(f"   Accuracy: {row['metrics.test_accuracy']:.4f}")
        print()

def ejemplo_3_comparar_configuraciones():
    """Ejemplo 3: Comparar runs con/sin augmentation"""
    print("\n" + "="*80)
    print("EJEMPLO 3: Comparar Configuraciones (Augmentation vs No Augmentation)")
    print("="*80)
    
    exp = mlflow.get_experiment_by_name("deteccion_arritmias_ecg")
    
    if not exp:
        print("⚠️  Experimento no existe")
        return
    
    # Buscar runs con augmentation
    runs_aug = mlflow.search_runs(
        experiment_ids=[exp.experiment_id],
        filter_string="params.use_augment = 'True'",
        max_results=10
    )
    
    # Buscar runs sin augmentation
    runs_no_aug = mlflow.search_runs(
        experiment_ids=[exp.experiment_id],
        filter_string="params.use_augment = 'False'",
        max_results=10
    )
    
    print(f"\nRuns CON augmentation: {len(runs_aug)}")
    if not runs_aug.empty and 'metrics.test_f1_V' in runs_aug.columns:
        print(f"  F1 Score promedio: {runs_aug['metrics.test_f1_V'].mean():.4f}")
        print(f"  F1 Score máximo: {runs_aug['metrics.test_f1_V'].max():.4f}")
    
    print(f"\nRuns SIN augmentation: {len(runs_no_aug)}")
    if not runs_no_aug.empty and 'metrics.test_f1_V' in runs_no_aug.columns:
        print(f"  F1 Score promedio: {runs_no_aug['metrics.test_f1_V'].mean():.4f}")
        print(f"  F1 Score máximo: {runs_no_aug['metrics.test_f1_V'].max():.4f}")
    
    if not runs_aug.empty and not runs_no_aug.empty:
        if 'metrics.test_f1_V' in runs_aug.columns and 'metrics.test_f1_V' in runs_no_aug.columns:
            diff = runs_aug['metrics.test_f1_V'].mean() - runs_no_aug['metrics.test_f1_V'].mean()
            print(f"\n📊 Diferencia: {diff:+.4f} ({diff*100:+.2f}%)")
            
            if diff > 0:
                print("   ✅ Augmentation mejora el rendimiento")
            else:
                print("   ❌ Augmentation NO mejora el rendimiento")

def ejemplo_4_cargar_modelo():
    """Ejemplo 4: Cargar el mejor modelo"""
    print("\n" + "="*80)
    print("EJEMPLO 4: Cargar Mejor Modelo")
    print("="*80)
    
    exp = mlflow.get_experiment_by_name("deteccion_arritmias_ecg")
    
    if not exp:
        print("⚠️  Experimento no existe")
        return
    
    # Buscar mejor run
    runs = mlflow.search_runs(
        experiment_ids=[exp.experiment_id],
        order_by=["metrics.test_f1_V DESC"],
        max_results=1
    )
    
    if runs.empty:
        print("⚠️  No hay runs registrados")
        return
    
    best_run_id = runs.iloc[0]['run_id']
    
    print(f"\n🏆 Mejor Run ID: {best_run_id}")
    
    if 'metrics.test_f1_V' in runs.columns:
        print(f"   F1 Score: {runs.iloc[0]['metrics.test_f1_V']:.4f}")
    
    print(f"\n📦 Para cargar este modelo en Python:")
    print(f"```python")
    print(f"import mlflow")
    print(f"model = mlflow.keras.load_model('runs:/{best_run_id}/model')")
    print(f"predictions = model.predict({{'sig': X_sig, 'rr': X_rr}})")
    print(f"```")
    
    # Mostrar parámetros del mejor modelo
    print(f"\n⚙️  Hiperparámetros del mejor modelo:")
    param_cols = [c for c in runs.columns if c.startswith('params.')]
    for col in param_cols[:10]:  # Primeros 10
        param_name = col.replace('params.', '')
        value = runs.iloc[0][col]
        print(f"   {param_name}: {value}")

def ejemplo_5_estadisticas_generales():
    """Ejemplo 5: Estadísticas generales de todos los experimentos"""
    print("\n" + "="*80)
    print("EJEMPLO 5: Estadísticas Generales")
    print("="*80)
    
    exp = mlflow.get_experiment_by_name("deteccion_arritmias_ecg")
    
    if not exp:
        print("⚠️  Experimento no existe")
        return
    
    runs = mlflow.search_runs(experiment_ids=[exp.experiment_id])
    
    if runs.empty:
        print("⚠️  No hay runs")
        return
    
    print(f"\n📊 Total de experimentos: {len(runs)}")
    
    # Estadísticas de métricas
    metrics = ['test_accuracy', 'test_precision_V', 'test_recall_V', 'test_f1_V']
    
    print("\n📈 Estadísticas de Métricas:\n")
    
    for metric in metrics:
        col = f'metrics.{metric}'
        if col in runs.columns:
            data = runs[col].dropna()
            if len(data) > 0:
                print(f"{metric}:")
                print(f"  Media:   {data.mean():.4f}")
                print(f"  Mediana: {data.median():.4f}")
                print(f"  Std:     {data.std():.4f}")
                print(f"  Min:     {data.min():.4f}")
                print(f"  Max:     {data.max():.4f}")
                print()

def main():
    """Ejecuta todos los ejemplos"""
    print("\n" + "="*80)
    print("🚀 EJEMPLOS DE USO DE MLflow")
    print("="*80)
    
    # Setup MLflow
    setup_mlflow()
    
    # Ejecutar ejemplos
    ejemplo_1_listar_experimentos()
    ejemplo_2_buscar_mejores_modelos()
    ejemplo_3_comparar_configuraciones()
    ejemplo_4_cargar_modelo()
    ejemplo_5_estadisticas_generales()
    
    print("\n" + "="*80)
    print("✅ EJEMPLOS COMPLETADOS")
    print("="*80)
    print("\n💡 Para ver más detalles, abre MLflow UI:")
    print("   .\start_mlflow.ps1")
    print("   O: mlflow ui")
    print("\n📚 Consulta MLOPS_GUIDE.md para más información")
    print()

if __name__ == "__main__":
    main()
