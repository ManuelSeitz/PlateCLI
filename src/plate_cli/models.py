from typing import Any, List, cast

import easyocr
import numpy as np
from cv2.typing import MatLike
from easyocr.easyocr import Reader
from PIL.Image import Image
from PIL.ImageFile import ImageFile
from ultralytics.engine.results import Boxes, Results
from ultralytics.models import YOLO

from plate_cli.constants import (
    CONF_THRESHOLD,
    NMS_THRESHOLD,
    OCR_BLOCKLIST,
    YOLO_MODEL_PATH,
)
from plate_cli.utils.normalize import normalize_text
from plate_cli.utils.preprocess_image import preprocess_image


class Models:
    def __init__(self) -> None:
        self.yolo: YOLO | None = None
        self.reader: Reader | None = None

    def load_yolo(self) -> None:
        self.yolo = YOLO(YOLO_MODEL_PATH)

    def load_reader(self) -> None:
        self.reader = easyocr.Reader(["es", "pt"], gpu=True, verbose=False)

    def inference(self, image: ImageFile | MatLike, **kwargs: Any) -> List[Results]:
        if self.yolo is None:
            raise RuntimeError("El modelo YOLO no ha sido cargado.")
        results = cast(
            List[Results],
            self.yolo(
                image, verbose=False, conf=CONF_THRESHOLD, iou=NMS_THRESHOLD, **kwargs
            ),
        )
        return results

    def get_text_from_image(self, image: Image, box: Boxes, country: str) -> str:
        x_min, y_min, x_max, y_max = cast(List[float], box.xyxy[0].tolist())  # type: ignore
        crop = image.crop((x_min, y_min, x_max, y_max))
        np_crop = np.array(crop)

        preprocessed = preprocess_image(np_crop, country)

        text = self.reader.readtext(  # type: ignore
            preprocessed,
            detail=0,
            paragraph=True,
            blocklist=OCR_BLOCKLIST,
        )

        if not text:
            return ""

        normalized_text = normalize_text(cast(str, text[-1]), country)

        return normalized_text
