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

YOLO_MODEL_PATH = (Path(__file__).parent / "../../weights/v1/model.pt").resolve()

OCR_BLOCKLIST = "¡!¿?@#$%&/()=?¿[]{}.,;:_+'*<>|°\"\\"
