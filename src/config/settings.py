## src/config/settings.py
from dotenv import load_dotenv
import os
from pathlib import Path

# Obtener la ruta base del proyecto (un nivel arriba de src)
BASE_DIR = Path(__file__).parent.parent.parent

# Cargar variables de entorno
load_dotenv(BASE_DIR / '.env')

# Configuración
EMAIL = os.getenv('HF_EMAIL')
PASSWD = os.getenv('HF_PASSWORD')
COOKIE_PATH = BASE_DIR / 'data' / 'cookies'

# Validación
if not all([EMAIL, PASSWD]):
    raise ValueError(
        "Variables de entorno requeridas no encontradas. "
        "Asegúrate de que HUGGING_EMAIL y HUGGING_PASSWORD "
        "estén definidas en el archivo .env"
    )

# Crear directorio de cookies si no existe
COOKIE_PATH.mkdir(parents=True, exist_ok=True)
