from typing import cast

import cv2
from cv2.typing import MatLike
from PIL import Image
from rich.live import Live
from rich.table import Table
from ultralytics.engine.results import Results

from utils.detections.label import get_label
from utils.detections.ocr import run_ocr
from utils.error import show_error
from utils.models import load_models
from utils.panel import get_panel


def open_camera():
    capture = cv2.VideoCapture(0)
    if not capture.isOpened():
        show_error(":x: No se pudo abrir la cámara")
        return

    table = Table(title="Detección en tiempo real", show_header=True)
    table.add_column("País", style="cyan")
    table.add_column("Matrícula", style="magenta")
    table.add_column("Confianza", style="green")

    with Live(
        get_panel(table, title="PlateCLI"),
        screen=False,
        refresh_per_second=4,
    ) as live:
        try:
            detect_plates(capture, live, table)
        finally:
            capture.release()
            cv2.destroyAllWindows()


def detect_plates(capture: cv2.VideoCapture, live: Live, table: Table):
    model, reader = load_models()

    while True:
        return_value, frame = capture.read()
        if not return_value:
            break

        results = cast(Results, model(frame, verbose=False, stream=True))

        for result in results:
            if result.boxes:
                box = result.boxes[0]

                # Convertir frame a imagen RGB y luego a imagen PIL para usarse en el OCR
                img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(img_rgb)

                text = run_ocr(reader, pil_img, box)

                draw_box(frame, result, text)

                conf = f"{box.conf.item():.2f}"
                class_name = result.names[int(box.cls.item())]
                table.add_row(class_name, text, conf)
                live.update(get_panel(table, title="PlateCLI"))

        cv2.imshow("Presiona 'q' para salir", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


def draw_box(frame: MatLike, result: Results, text: str):
    if not result.boxes:
        return

    box = result.boxes.xyxy[0]
    x1, y1, x2, y2 = (int(box[0]), int(box[1]), int(box[2]), int(box[3]))

    # Dibujar bbox
    cv2.rectangle(frame, (x1, y1), (x2, y2), (135, 0, 0), 2)

    # Dibujar label
    label = get_label(text, result)
    (w, _), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
    cv2.rectangle(frame, (x1, y1 - 25), (x1 + w, y1), (135, 0, 0), -1)
    cv2.putText(
        frame,
        label,
        (x1, y1 - 7),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        1,
    )
