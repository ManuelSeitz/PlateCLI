from pathlib import Path
from typing import List, cast

from easyocr.easyocr import Reader
from PIL import Image, ImageDraw, ImageFile, ImageFont
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.spinner import Spinner
from ultralytics.engine.results import Results
from ultralytics.models import YOLO

from utils.constants import ACCEPTED_IMAGE_FORMATS
from utils.detections.label import get_label
from utils.detections.ocr import run_ocr
from utils.error import show_error
from utils.models import load_models
from utils.panel import get_panel
from utils.prompt import Prompt

console = Console()


def load_images():
    prompt = Prompt("Seleccionar lote o imagen")
    path = prompt.ask()
    if path is None:
        return
    process_path(path)


def process_path(dir_path: str):
    path = Path(dir_path)

    model, reader = load_models()

    if not path.exists():
        show_error(":x: El directorio no existe")
        return

    if path.is_file():
        if path.suffix not in ACCEPTED_IMAGE_FORMATS:
            show_error(":x: Extensión no soportada")
            return
        detect_plate(model, reader, path)


def detect_plate(model: YOLO, reader: Reader, image_path: Path) -> None:
    loading_content = Group(
        Spinner("dots", text="[bold]Detectando matrícula..."),
    )

    panel = get_panel(loading_content, width=60, expand=True)

    with Live(panel, refresh_per_second=10, screen=True) as live:
        results = cast(List[Results], model(image_path, verbose=False))
        result = results[0]
        processing_content = Group(
            "[green]✓ Matrícula detectada exitosamente",
        )

        live.update(get_panel(processing_content, width=60, expand=True))

    if not result.boxes:
        return

    image = Image.open(image_path)
    text = run_ocr(reader, image, result.boxes[0])

    draw_box(image, result, text)

    class_id = int(result.boxes[0].cls.item())
    class_name = result.names[class_id]
    new_filename = f"{class_name}_{text.replace(' ', '_')}.jpg"

    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)

    save_path = output_dir / new_filename

    image.save(save_path)

    saved_file_path = save_path.resolve()

    console.print(
        Panel(
            f"[bold green]✓[/] Imagen guardada en: [cyan]{saved_file_path}",
            border_style="green",
            expand=False,
        )
    )


def draw_box(image: ImageFile.ImageFile, result: Results, text: str):
    draw = ImageDraw.Draw(image)

    if not result.boxes:
        return

    box = result.boxes.xyxy[0]
    x1, y1, x2, y2 = float(box[0]), float(box[1]), float(box[2]), float(box[3])

    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except (OSError, IOError):
        font = ImageFont.load_default(28)

    # Dibujar bbox
    draw.rectangle([x1, y1, x2, y2], outline="#000087", width=4)

    label = get_label(text, result)

    # Obtener bbox del label
    left, top, right, bottom = draw.textbbox((x1, y1), label, font=font)

    text_height = bottom - top
    text_width = right - left

    # Dimensiones del rectángulo de fondo
    bg_rect = [x1, y1 - text_height - 5, x1 + text_width + 5, y1]

    draw.rectangle(bg_rect, fill="#000087")
    draw.text((x1 + 2, y1 - text_height - 5), label, fill="white", font=font)
