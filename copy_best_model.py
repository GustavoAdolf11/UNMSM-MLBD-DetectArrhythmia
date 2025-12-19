"""
Script para copiar el mejor modelo de MLflow a producción
"""
import mlflow
import shutil
from pathlib import Path
import json

# Configurar MLflow
mlflow.set_tracking_uri('file:./mlruns')

# Buscar experimento
exp = mlflow.get_experiment_by_name('deteccion_arritmias_ecg')
if not exp:
    print('❌ No hay experimentos registrados')
    print('💡 Ejecuta primero: python deteccionarritmias.py')
    exit(1)

# Buscar mejor modelo por F1-Score de clase V
runs = mlflow.search_runs(
    experiment_ids=[exp.experiment_id],
    order_by=['metrics.test_f1_V DESC'],
    max_results=1
)

if runs.empty:
    print('❌ No hay runs registrados')
    exit(1)

best_run = runs.iloc[0]

# Mostrar métricas
print('✅ Mejor modelo encontrado:')
print(f'   Run ID: {best_run["run_id"]}')
print(f'   F1-Score V: {best_run["metrics.test_f1_V"]:.4f}')
print(f'   Accuracy: {best_run["metrics.test_accuracy"]:.4f}')
print(f'   Precision V: {best_run["metrics.test_precision_V"]:.4f}')
print(f'   Recall V: {best_run["metrics.test_recall_V"]:.4f}')

# Copiar modelo
model_src = Path(f'mlruns/{exp.experiment_id}/{best_run["run_id"]}/artifacts/models/model_v7.keras')
model_dst = Path('models/ecg_nv_cnn/model_v7.keras')

model_dst.parent.mkdir(parents=True, exist_ok=True)

if model_src.exists():
    shutil.copy(model_src, model_dst)
    print(f'✅ Modelo copiado a {model_dst}')
else:
    print(f'❌ Modelo no encontrado en {model_src}')
    exit(1)

# Guardar métricas para el commit
metrics_info = {
    'run_id': best_run["run_id"],
    'f1_v': float(best_run["metrics.test_f1_V"]),
    'accuracy': float(best_run["metrics.test_accuracy"]),
    'precision_v': float(best_run["metrics.test_precision_V"]),
    'recall_v': float(best_run["metrics.test_recall_V"])
}

with open('.mlflow_deploy_metrics.json', 'w') as f:
    json.dump(metrics_info, f, indent=2)

print('✅ Métricas guardadas para deployment')
