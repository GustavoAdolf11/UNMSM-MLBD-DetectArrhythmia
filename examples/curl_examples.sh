"""
Test the API with curl commands (for reference)
"""

# Health Check
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000/

# Predict arrhythmia (with test data)
curl -X POST "http://localhost:8000/api/v1/predictions/" \
  -H "Content-Type: application/json" \
  -d '{
    "signal_data": [0.1, 0.15, 0.2, 0.18, 0.12, 0.08, 0.05, 0.03, 0.02, 0.01],
    "sampling_rate": 360,
    "derivation": "MLII",
    "patient_id": "TEST001",
    "apply_ruleguard": true
  }'
