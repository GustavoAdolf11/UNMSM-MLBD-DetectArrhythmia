"""
Entry point para Hugging Face Spaces
Este archivo es requerido por Hugging Face para iniciar la aplicación.
"""
import os
import sys
from pathlib import Path

# Asegurar que el directorio raíz esté en el path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Importar la aplicación FastAPI
from src.presentation.app import create_app

# Crear la aplicación
app = create_app()

# Hugging Face Spaces espera que la app se llame 'app'
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))  # Hugging Face usa puerto 7860
    uvicorn.run(app, host="0.0.0.0", port=port)
