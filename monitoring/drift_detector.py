"""
Monitor de Data Drift para detección de cambios en distribuciones de datos ECG
Utiliza Evidently para detectar drift en features y predicciones
"""
import os
import json
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path

try:
    from evidently.report import Report
    from evidently.metric_preset import DataDriftPreset, TargetDriftPreset
    EVIDENTLY_AVAILABLE = True
except ImportError:
    EVIDENTLY_AVAILABLE = False
    print("⚠️  Evidently no está instalado. Instala con: pip install evidently")


class ECGDriftDetector:
    """Detector de drift para datos ECG"""
    
    def __init__(self, reference_data_path=None, report_dir="monitoring/reports"):
        self.reference_data = None
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        if reference_data_path:
            self.load_reference_data(reference_data_path)
    
    def load_reference_data(self, path):
        """Carga datos de referencia (baseline)"""
        if isinstance(path, (str, Path)):
            self.reference_data = pd.read_csv(path)
        elif isinstance(path, pd.DataFrame):
            self.reference_data = path
        else:
            raise ValueError("path debe ser str, Path o DataFrame")
        
        print(f"✅ Datos de referencia cargados: {len(self.reference_data)} muestras")
    
    def detect_drift(self, current_data, save_report=True):
        """
        Detecta drift entre datos de referencia y actuales
        
        Args:
            current_data: DataFrame con datos actuales
            save_report: Si guardar reporte HTML
        
        Returns:
            dict con resultados de drift
        """
        if not EVIDENTLY_AVAILABLE:
            raise ImportError("Evidently no está instalado")
        
        if self.reference_data is None:
            raise ValueError("Primero carga datos de referencia con load_reference_data()")
        
        # Crear reporte de drift
        report = Report(metrics=[
            DataDriftPreset(),
        ])
        
        report.run(
            reference_data=self.reference_data,
            current_data=current_data
        )
        
        # Extraer resultados
        results = report.as_dict()
        
        # Determinar si hay drift
        drift_detected = False
        drifted_features = []
        
        try:
            metrics = results['metrics']
            for metric in metrics:
                if 'result' in metric and 'dataset_drift' in metric['result']:
                    drift_detected = metric['result']['dataset_drift']
                if 'result' in metric and 'drift_by_columns' in metric['result']:
                    for col, drift_info in metric['result']['drift_by_columns'].items():
                        if drift_info.get('drift_detected', False):
                            drifted_features.append(col)
        except Exception as e:
            print(f"⚠️  Error extrayendo drift: {e}")
        
        # Guardar reporte HTML
        if save_report:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_path = self.report_dir / f"drift_report_{timestamp}.html"
            report.save_html(str(report_path))
            print(f"📄 Reporte guardado: {report_path}")
        
        drift_summary = {
            "drift_detected": drift_detected,
            "drifted_features": drifted_features,
            "num_drifted_features": len(drifted_features),
            "timestamp": datetime.now().isoformat(),
            "reference_size": len(self.reference_data),
            "current_size": len(current_data)
        }
        
        # Guardar resumen JSON
        summary_path = self.report_dir / f"drift_summary_{timestamp}.json"
        with open(summary_path, 'w') as f:
            json.dump(drift_summary, f, indent=2)
        
        if drift_detected:
            print("⚠️  DRIFT DETECTADO!")
            print(f"   Features afectados: {drifted_features}")
            self._trigger_alert(drift_summary)
        else:
            print("✅ No se detectó drift")
        
        return drift_summary
    
    def _trigger_alert(self, drift_info):
        """Dispara alerta cuando se detecta drift"""
        alert_file = self.report_dir / "drift_alerts.log"
        
        with open(alert_file, 'a') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"ALERTA DE DRIFT - {drift_info['timestamp']}\n")
            f.write(f"Features afectados: {drift_info['drifted_features']}\n")
            f.write(f"Total features con drift: {drift_info['num_drifted_features']}\n")
            f.write(f"{'='*80}\n")
        
        print(f"🔔 Alerta registrada en {alert_file}")
        # Aquí podrías agregar notificaciones por email, Slack, etc.


def create_sample_monitoring_data(n_samples=1000):
    """Crea datos de ejemplo para monitoreo"""
    rng = np.random.default_rng(42)
    
    df = pd.DataFrame({
        'rr_prev': rng.normal(0.8, 0.15, n_samples),
        'rr_next': rng.normal(0.8, 0.15, n_samples),
        'rr_ratio': rng.normal(1.0, 0.2, n_samples),
        'qrs_width': rng.normal(100, 20, n_samples),
        'prediction_proba': rng.beta(2, 5, n_samples),  # Más Ns que Vs
        'prediction': (rng.random(n_samples) > 0.8).astype(int)
    })
    
    return df


if __name__ == "__main__":
    print("🔍 Monitor de Data Drift - ECG Arritmias")
    print()
    
    if not EVIDENTLY_AVAILABLE:
        print("❌ Instala evidently primero: pip install evidently")
    else:
        # Ejemplo de uso
        print("📊 Generando datos de ejemplo...")
        reference = create_sample_monitoring_data(1000)
        current = create_sample_monitoring_data(1000)
        
        # Simular drift (cambiar distribución)
        current['rr_ratio'] = current['rr_ratio'] * 1.3  # Drift artificial
        
        detector = ECGDriftDetector()
        detector.load_reference_data(reference)
        
        print("\n🔍 Detectando drift...")
        results = detector.detect_drift(current)
        
        print("\n📈 Resultados:")
        print(json.dumps(results, indent=2))
