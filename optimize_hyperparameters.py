"""
Optimización de Hiperparámetros con Optuna + MLflow
Encuentra automáticamente la mejor configuración del modelo
"""
import os
import sys
import optuna
import mlflow
import mlflow.keras
import numpy as np
import pandas as pd
from datetime import datetime
from optuna.integration.mlflow import MLflowCallback

# Importar funciones del script principal
# (Asumiendo que deteccionarritmias.py tiene las funciones necesarias)

def objective(trial):
    """
    Función objetivo para Optuna
    Define el espacio de búsqueda de hiperparámetros
    """
    
    # Hiperparámetros a optimizar
    params = {
        'focal_gamma': trial.suggest_float('focal_gamma', 1.0, 3.0),
        'focal_alpha': trial.suggest_float('focal_alpha', 0.25, 0.45),
        'dropout_rate': trial.suggest_float('dropout_rate', 0.2, 0.5),
        'l2_reg': trial.suggest_float('l2_reg', 1e-5, 1e-3, log=True),
        'learning_rate': trial.suggest_float('learning_rate', 1e-4, 1e-2, log=True),
        'batch_size': trial.suggest_categorical('batch_size', [128, 256, 512]),
        'conv1_filters': trial.suggest_categorical('conv1_filters', [16, 32, 64]),
        'conv2_filters': trial.suggest_categorical('conv2_filters', [32, 64, 128]),
        'dense_units': trial.suggest_categorical('dense_units', [32, 64, 128])
    }
    
    # Aquí iría el código de entrenamiento usando estos parámetros
    # Por ahora retornamos un valor simulado
    # En producción, entrenarías el modelo y retornarías test_f1_V
    
    print(f"\n📊 Trial {trial.number} - Params: {params}")
    
    # SIMULACIÓN - Reemplazar con entrenamiento real
    # test_f1_V = train_model_with_params(params)
    test_f1_V = np.random.uniform(0.75, 0.92)  # Simulado
    
    return test_f1_V


def run_hyperparameter_optimization(n_trials=20):
    """
    Ejecuta optimización de hiperparámetros con Optuna
    
    Args:
        n_trials: Número de trials a ejecutar
    """
    
    # Configurar MLflow
    mlflow.set_tracking_uri("file:./mlruns")
    experiment_name = "hyperparameter_optimization"
    mlflow.set_experiment(experiment_name)
    
    # Callback para integrar con MLflow
    mlflc = MLflowCallback(
        tracking_uri="file:./mlruns",
        metric_name="f1_score",
        create_experiment=False
    )
    
    # Crear estudio de Optuna
    study = optuna.create_study(
        study_name=f"optuna_study_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        direction="maximize",  # Maximizar F1 score
        sampler=optuna.samplers.TPESampler(seed=42),
        pruner=optuna.pruners.MedianPruner(n_startup_trials=5)
    )
    
    print(f"🔬 Iniciando optimización de hiperparámetros")
    print(f"   Experimento: {experiment_name}")
    print(f"   Trials: {n_trials}")
    print(f"   Objetivo: Maximizar F1 Score (clase V)")
    print()
    
    # Optimizar
    study.optimize(
        objective,
        n_trials=n_trials,
        callbacks=[mlflc],
        show_progress_bar=True
    )
    
    # Resultados
    print("\n" + "="*80)
    print("✅ OPTIMIZACIÓN COMPLETADA")
    print("="*80)
    
    print(f"\n🏆 Mejores hiperparámetros:")
    for key, value in study.best_params.items():
        print(f"   {key}: {value}")
    
    print(f"\n📊 Mejor F1 Score: {study.best_value:.4f}")
    print(f"   Trial número: {study.best_trial.number}")
    
    # Guardar resultados
    results_dir = "optimization_results"
    os.makedirs(results_dir, exist_ok=True)
    
    # DataFrame con todos los trials
    df = study.trials_dataframe()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    df.to_csv(f"{results_dir}/optuna_trials_{timestamp}.csv", index=False)
    
    # Guardar mejores parámetros
    import json
    with open(f"{results_dir}/best_params_{timestamp}.json", 'w') as f:
        json.dump(study.best_params, f, indent=2)
    
    print(f"\n💾 Resultados guardados en: {results_dir}/")
    
    # Visualizaciones de Optuna
    try:
        import optuna.visualization as vis
        
        # Importancia de parámetros
        fig = vis.plot_param_importances(study)
        fig.write_html(f"{results_dir}/param_importance_{timestamp}.html")
        
        # Historia de optimización
        fig = vis.plot_optimization_history(study)
        fig.write_html(f"{results_dir}/optimization_history_{timestamp}.html")
        
        # Parallel coordinate plot
        fig = vis.plot_parallel_coordinate(study)
        fig.write_html(f"{results_dir}/parallel_coordinate_{timestamp}.html")
        
        print(f"📈 Visualizaciones guardadas en: {results_dir}/")
        
    except Exception as e:
        print(f"⚠️  Error generando visualizaciones: {e}")
    
    return study


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Optimización de hiperparámetros con Optuna')
    parser.add_argument('--trials', type=int, default=20, help='Número de trials (default: 20)')
    args = parser.parse_args()
    
    study = run_hyperparameter_optimization(n_trials=args.trials)
    
    print("\n" + "="*80)
    print("🎯 PRÓXIMOS PASOS:")
    print("="*80)
    print("1. Revisa los resultados en: optimization_results/")
    print("2. Actualiza deteccionarritmias.py con los mejores parámetros")
    print("3. Entrena el modelo final")
    print("4. Visualiza en MLflow UI: mlflow ui")
    print()
