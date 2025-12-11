"""
Example usage of the ECG Arrhythmia Detection API
"""
import requests
import numpy as np
import wfdb
import os


def example_with_synthetic_signal():
    """Ejemplo con señal sintética."""
    print("📊 Generando señal sintética...")
    
    # Generar señal sinusoidal simple (10 segundos @ 360 Hz)
    duration = 10  # segundos
    fs = 360
    t = np.linspace(0, duration, duration * fs)
    
    # Simular ECG: componente de frecuencia cardíaca (~1 Hz)
    signal = np.sin(2 * np.pi * 1.2 * t) + 0.3 * np.sin(2 * np.pi * 3 * t)
    signal = signal.tolist()
    
    print(f"✅ Señal generada: {len(signal)} muestras")
    
    # Hacer request a la API
    print("\n🚀 Enviando request a la API...")
    response = requests.post(
        "http://localhost:8000/api/v1/predictions/",
        json={
            "signal_data": signal,
            "sampling_rate": 360,
            "derivation": "MLII",
            "patient_id": "TEST001",
            "apply_ruleguard": True
        }
    )
    
    if response.status_code == 201:
        result = response.json()
        print("\n✅ Predicción exitosa!")
        print(f"  🆔 Prediction ID: {result['prediction_id']}")
        print(f"  📈 Tipo: {result['overall_arrhythmia_type']}")
        print(f"  🎯 Confianza: {result['overall_confidence']:.2%}")
        print(f"  ⚠️  Nivel de riesgo: {result['risk_level']}")
        print(f"  💓 Total latidos: {result['total_beats']}")
        print(f"  ✅ Normal: {result['normal_beats']}")
        print(f"  ⚡ Ventricular: {result['ventricular_beats']}")
        print(f"  ⏱️  Tiempo: {result['processing_time_ms']:.1f}ms")
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.json())


def example_with_mitbih_record():
    """Ejemplo con registro real de MIT-BIH."""
    print("📊 Cargando registro MIT-BIH...")
    
    # Cargar un registro de ejemplo (record 100)
    base_path = os.path.join(os.path.dirname(__file__), 'mit-bih')
    record_id = '100'
    
    try:
        record = wfdb.rdrecord(os.path.join(base_path, record_id))
        
        # Tomar primeros 10 segundos del canal MLII (índice 0)
        duration = 10
        samples = duration * record.fs
        signal = record.p_signal[:samples, 0].tolist()
        
        print(f"✅ Registro {record_id} cargado: {len(signal)} muestras")
        
        # Hacer request
        print("\n🚀 Enviando request a la API...")
        response = requests.post(
            "http://localhost:8000/api/v1/predictions/",
            json={
                "signal_data": signal,
                "sampling_rate": record.fs,
                "derivation": "MLII",
                "patient_id": record_id,
                "apply_ruleguard": True
            }
        )
        
        if response.status_code == 201:
            result = response.json()
            print("\n✅ Predicción exitosa!")
            print(f"  🆔 Prediction ID: {result['prediction_id']}")
            print(f"  📈 Tipo: {result['overall_arrhythmia_type']}")
            print(f"  🎯 Confianza: {result['overall_confidence']:.2%}")
            print(f"  ⚠️  Nivel de riesgo: {result['risk_level']}")
            print(f"  💓 Total latidos: {result['total_beats']}")
            print(f"  ✅ Normal: {result['normal_beats']}")
            print(f"  ⚡ Ventricular: {result['ventricular_beats']}")
            print(f"  ⏱️  Tiempo: {result['processing_time_ms']:.1f}ms")
            
            # Mostrar algunos latidos
            print("\n📋 Primeros 5 latidos:")
            for beat in result['beat_predictions'][:5]:
                print(f"  Beat {beat['beat_index']}: {beat['arrhythmia_type']} "
                      f"(conf: {beat['confidence']:.2%}, pos: {beat['position_sample']})")
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.json())
            
    except Exception as e:
        print(f"❌ Error cargando registro: {e}")
        print("💡 Intenta con el ejemplo sintético")


def check_api_health():
    """Verifica el estado de la API."""
    print("🏥 Verificando health check...")
    
    try:
        response = requests.get("http://localhost:8000/health")
        
        if response.status_code == 200:
            health = response.json()
            print(f"✅ API Status: {health['status']}")
            print(f"📦 Version: {health['version']}")
            print(f"🤖 Model loaded: {health['model_loaded']}")
        else:
            print(f"❌ API no responde correctamente: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar a la API")
        print("💡 Asegúrate de que el servidor esté corriendo: python main.py")


if __name__ == "__main__":
    print("=" * 60)
    print("ECG Arrhythmia Detection API - Ejemplos de Uso")
    print("=" * 60)
    
    # 1. Health check
    check_api_health()
    print("\n" + "=" * 60 + "\n")
    
    # 2. Ejemplo con señal sintética
    example_with_synthetic_signal()
    print("\n" + "=" * 60 + "\n")
    
    # 3. Ejemplo con MIT-BIH (opcional)
    # Descomenta para probar con datos reales:
    # example_with_mitbih_record()
