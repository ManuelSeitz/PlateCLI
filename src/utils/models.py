from typing import Tuple

import easyocr
from easyocr.easyocr import Reader
from rich.console import Group
from rich.live import Live
from rich.spinner import Spinner
from ultralytics.models import YOLO

from utils.constants import YOLO_MODEL_PATH
from utils.panel import get_panel


def load_models() -> Tuple[YOLO, Reader]:
    loading_content = Group(Spinner("dots", text="[bold]Cargando modelo..."))

    panel = get_panel(loading_content, width=60, expand=True)

    with Live(panel, refresh_per_second=10, screen=True) as live:
        model = YOLO(YOLO_MODEL_PATH)
        content = Group(
            "[green]✓ Modelo cargado exitosamente",
            Spinner("dots", text="[bold]Cargando OCR..."),
        )
        live.update(get_panel(content, width=60, expand=True))
        reader = easyocr.Reader(["es", "pt"], gpu=False, verbose=False)

    return model, reader
