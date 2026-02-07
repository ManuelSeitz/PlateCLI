from pathlib import Path
from typing import Dict

ACCEPTED_IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".webp"]

COUNTRIES: Dict[str, str] = {
    "argentina": "buenosaires",
    "bolivia": "lapaz",
    "brazil": "riodejaneiro",
    "chile": "santiagocl",
    "colombia": "bogota",
    "costa-rica": "sanjosecr",
    "ecuador": "quito",
    "guatemala": "guatemalacity",
    "mexico": "mexicocity",
    "paraguay": "asuncion",
    "peru": "lima",
    "uruguay": "montevideo",
    "venezuela": "caracas",
}

YOLO_MODEL_PATH = (Path(__file__).parent / "models/v1/weights.pt").resolve()

CONF_THRESHOLD = 0.63  # Limita el nivel de confianza aceptable
NMS_THRESHOLD = 0.5  # Evita detecciones solapadas

OCR_BLOCKLIST = (
    "¡!¿?@#$%&/()=?¿[]{}-.,;:_+'*<>|°\"\\"
    "áéíóúÁÉÍÓÚàèìòùÀÈÌÒÙâêîôûÂÊÎÔÛäëïöüÄËÏÖÜ"
    "ñÑçÇ"
    "¬~`^"
    "€£¥$¢"
    "±÷×¶§©®™ª"
)
