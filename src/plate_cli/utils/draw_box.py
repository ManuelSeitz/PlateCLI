import cv2
import numpy as np
from ultralytics.engine.results import Results


def draw_box(image: np.ndarray, result: Results, text: str):
    if not result.boxes:
        return image

    box = result.boxes.xyxy[0].cpu().numpy()
    x1, y1, x2, y2 = map(int, box[:4])

    conf = float(result.boxes.conf[0])
    class_id = int(result.boxes[0].cls.item())
    class_name = result.names[class_id]
    label = f"{class_name}: {text} ({conf:.2f})"

    # Configuración de estilo
    color_rgb = (0, 0, 135)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.8
    thickness = 2

    # Dibujar bbox
    cv2.rectangle(image, (x1, y1), (x2, y2), color_rgb, 4)

    (w, h), _ = cv2.getTextSize(label, font, font_scale, thickness)

    # Dibujar fondo de texto
    cv2.rectangle(image, (x1, y1 - h - 10), (x1 + w, y1), color_rgb, -1)

    # Colocar texto
    cv2.putText(
        image, label, (x1, y1 - 7), font, font_scale, (255, 255, 255), thickness
    )

    return image
