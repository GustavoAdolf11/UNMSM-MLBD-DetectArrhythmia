"""
Script para comparar modelos y generar reportes de performance
"""
import mlflow
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime

class ModelComparator:
    """Compara múltiples runs de MLflow y genera reportes"""
    
    def __init__(self, experiment_name="deteccion_arritmias_ecg"):
        mlflow.set_tracking_uri("file:./mlruns")
        self.experiment = mlflow.get_experiment_by_name(experiment_name)
        if not self.experiment:
            raise ValueError(f"Experimento '{experiment_name}' no encontrado")
        
        self.experiment_id = self.experiment.experiment_id
        self.experiment_name = experiment_name
    
    def get_all_runs(self, filter_string=None, max_results=100):
        """Obtiene todos los runs del experimento"""
        runs = mlflow.search_runs(
            experiment_ids=[self.experiment_id],
            filter_string=filter_string,
            max_results=max_results,
            order_by=["metrics.test_f1_V DESC"]
        )
        return runs
    
    def get_top_models(self, n=5, metric="metrics.test_f1_V"):
        """Obtiene los top N modelos según una métrica"""
        runs = self.get_all_runs(max_results=n)
        
        if runs.empty:
            print("⚠️  No hay runs disponibles")
            return None
        
        # Seleccionar columnas relevantes
        cols = [
            'run_id', 'start_time',
            'metrics.test_accuracy',
            'metrics.test_precision_V',
            'metrics.test_recall_V',
            'metrics.test_f1_V',
            'params.use_augment',
            'params.use_ruleguard'
        ]
        
        available_cols = [c for c in cols if c in runs.columns]
        top_runs = runs[available_cols].head(n)
        
        return top_runs
    
    def compare_models(self, run_ids):
        """Compara modelos específicos por run_id"""
        if not run_ids:
            print("⚠️  No hay run_ids para comparar")
            return None
        
        filter_str = " or ".join([f"run_id = '{rid}'" for rid in run_ids])
        runs = self.get_all_runs(filter_string=filter_str)
        
        return runs
    
    def generate_comparison_report(self, output_dir="reports"):
        """Genera reporte completo de comparación"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        runs = self.get_all_runs()
        
        if runs.empty:
            print("⚠️  No hay runs para generar reporte")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 1. Tabla resumen
        print(f"\n📊 Generando reporte de comparación...")
        
        summary_cols = [
            'run_id', 'start_time',
            'metrics.test_accuracy',
            'metrics.test_precision_V',
            'metrics.test_recall_V',
            'metrics.test_f1_V',
            'metrics.test_FP',
            'metrics.test_FN'
        ]
        
        available_cols = [c for c in summary_cols if c in runs.columns]
        summary = runs[available_cols].copy()
        summary.to_csv(output_path / f"model_comparison_{timestamp}.csv", index=False)
        
        # 2. Visualizaciones
        self._plot_metrics_comparison(runs, output_path, timestamp)
        
        # 3. Reporte de texto
        self._generate_text_report(runs, output_path, timestamp)
        
        print(f"✅ Reporte generado en: {output_path}/")
        print(f"   - model_comparison_{timestamp}.csv")
        print(f"   - metrics_comparison_{timestamp}.png")
        print(f"   - comparison_report_{timestamp}.txt")
    
    def _plot_metrics_comparison(self, runs, output_path, timestamp):
        """Genera gráficas de comparación"""
        metric_cols = [
            'metrics.test_accuracy',
            'metrics.test_precision_V',
            'metrics.test_recall_V',
            'metrics.test_f1_V'
        ]
        
        available_metrics = [c for c in metric_cols if c in runs.columns]
        
        if not available_metrics:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.flatten()
        
        for idx, metric in enumerate(available_metrics):
            ax = axes[idx]
            data = runs[metric].dropna()
            
            ax.hist(data, bins=20, edgecolor='black', alpha=0.7)
            ax.axvline(data.mean(), color='red', linestyle='--', label=f'Media: {data.mean():.3f}')
            ax.set_title(metric.replace('metrics.test_', '').replace('_', ' ').title())
            ax.set_xlabel('Valor')
            ax.set_ylabel('Frecuencia')
            ax.legend()
            ax.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path / f"metrics_comparison_{timestamp}.png", dpi=300)
        plt.close()
    
    def _generate_text_report(self, runs, output_path, timestamp):
        """Genera reporte de texto"""
        report_path = output_path / f"comparison_report_{timestamp}.txt"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("REPORTE DE COMPARACIÓN DE MODELOS\n")
            f.write(f"Experimento: {self.experiment_name}\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Total de runs: {len(runs)}\n\n")
            
            # Estadísticas
            metric_cols = [c for c in runs.columns if c.startswith('metrics.test_')]
            
            f.write("ESTADÍSTICAS DE MÉTRICAS:\n")
            f.write("-"*80 + "\n")
            
            for col in metric_cols:
                data = runs[col].dropna()
                if len(data) > 0:
                    f.write(f"\n{col.replace('metrics.test_', '')}:\n")
                    f.write(f"  Media: {data.mean():.4f}\n")
                    f.write(f"  Mediana: {data.median():.4f}\n")
                    f.write(f"  Std: {data.std():.4f}\n")
                    f.write(f"  Min: {data.min():.4f}\n")
                    f.write(f"  Max: {data.max():.4f}\n")
            
            # Top 5 modelos
            f.write("\n" + "="*80 + "\n")
            f.write("TOP 5 MODELOS (por F1 Score):\n")
            f.write("-"*80 + "\n\n")
            
            top5 = self.get_top_models(n=5)
            if top5 is not None:
                f.write(top5.to_string())
            
            f.write("\n\n" + "="*80 + "\n")


if __name__ == "__main__":
    print("📊 Comparador de Modelos MLflow\n")
    
    comparator = ModelComparator()
    
    # Ver top 5 modelos
    print("🏆 Top 5 Modelos:")
    print("="*80)
    top_models = comparator.get_top_models(n=5)
    if top_models is not None:
        print(top_models.to_string(index=False))
    
    # Generar reporte completo
    print("\n📈 Generando reporte completo...")
    comparator.generate_comparison_report()
    
    print("\n✅ Comparación completada")
    print("   Para más detalles, revisa la carpeta: reports/")
