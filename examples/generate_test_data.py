"""
Script to generate valid test data for ECG API testing.
Generates synthetic ECG signal with proper length (10 seconds at 360 Hz = 3600 samples).
"""
import json
import numpy as np

def generate_synthetic_ecg(duration_seconds=10, sampling_rate=360):
    """
    Generate synthetic ECG signal that mimics normal rhythm.
    
    Args:
        duration_seconds: Duration in seconds (default 10 for minimum required)
        sampling_rate: Sampling rate in Hz (default 360)
    
    Returns:
        List of float values representing ECG signal
    """
    num_samples = duration_seconds * sampling_rate
    time = np.linspace(0, duration_seconds, num_samples)
    
    # Generate synthetic ECG with P, QRS, T waves
    # Heart rate: ~75 bpm (0.8 seconds per beat)
    heart_rate = 75  # bpm
    beat_interval = 60.0 / heart_rate  # seconds between beats
    
    signal = np.zeros(num_samples)
    
    for i in range(int(duration_seconds / beat_interval) + 1):
        beat_time = i * beat_interval
        
        # P wave (atrial depolarization)
        p_center = beat_time + 0.08
        signal += 0.15 * np.exp(-((time - p_center) ** 2) / (2 * 0.01 ** 2))
        
        # Q wave (small negative deflection)
        q_center = beat_time + 0.16
        signal -= 0.05 * np.exp(-((time - q_center) ** 2) / (2 * 0.005 ** 2))
        
        # R wave (main peak)
        r_center = beat_time + 0.18
        signal += 1.2 * np.exp(-((time - r_center) ** 2) / (2 * 0.008 ** 2))
        
        # S wave (negative deflection after R)
        s_center = beat_time + 0.20
        signal -= 0.1 * np.exp(-((time - s_center) ** 2) / (2 * 0.005 ** 2))
        
        # T wave (ventricular repolarization)
        t_center = beat_time + 0.35
        signal += 0.25 * np.exp(-((time - t_center) ** 2) / (2 * 0.02 ** 2))
    
    # Add small random noise
    noise = np.random.normal(0, 0.02, num_samples)
    signal += noise
    
    return signal.tolist()


def create_test_payload(duration_seconds=10):
    """
    Create complete JSON payload for API testing.
    
    Args:
        duration_seconds: Duration in seconds (minimum 10)
    """
    signal_data = generate_synthetic_ecg(duration_seconds)
    
    payload = {
        "signal_data": signal_data,
        "sampling_rate": 360,
        "derivation": "MLII",
        "patient_id": "TEST001",
        "apply_ruleguard": True
    }
    
    return payload


def main():
    print("=" * 60)
    print("ECG API Test Data Generator")
    print("=" * 60)
    
    # Generate 10-second signal (minimum required)
    print("\nGenerating 10-second ECG signal (3600 samples)...")
    payload_10s = create_test_payload(10)
    
    print(f"✓ Generated {len(payload_10s['signal_data'])} samples")
    print(f"✓ Duration: 10 seconds")
    print(f"✓ Sampling rate: 360 Hz")
    
    # Save to file
    output_file = "test_payload_10s.json"
    with open(output_file, 'w') as f:
        json.dump(payload_10s, f, indent=2)
    
    print(f"\n✓ Saved to: {output_file}")
    
    # Also generate a 30-second version for more robust testing
    print("\nGenerating 30-second ECG signal (10800 samples)...")
    payload_30s = create_test_payload(30)
    
    print(f"✓ Generated {len(payload_30s['signal_data'])} samples")
    print(f"✓ Duration: 30 seconds")
    
    output_file_30s = "test_payload_30s.json"
    with open(output_file_30s, 'w') as f:
        json.dump(payload_30s, f, indent=2)
    
    print(f"✓ Saved to: {output_file_30s}")
    
    # Print sample for quick copy-paste (first 100 values)
    print("\n" + "=" * 60)
    print("Sample preview (first 100 values):")
    print("=" * 60)
    print(json.dumps(payload_10s['signal_data'][:100], indent=2))
    print("...")
    print(f"(continues for {len(payload_10s['signal_data'])} total samples)")
    
    print("\n" + "=" * 60)
    print("How to use:")
    print("=" * 60)
    print("1. Open test_payload_10s.json")
    print("2. Copy the entire content")
    print("3. Paste into Swagger UI request body")
    print("4. Click 'Execute'")
    print("\nOr use curl:")
    print('curl -X POST "http://localhost:8000/api/v1/predictions/" ^')
    print('  -H "Content-Type: application/json" ^')
    print('  -d @test_payload_10s.json')
    print("=" * 60)


if __name__ == "__main__":
    main()
