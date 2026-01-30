from typing import List, cast

import numpy as np
from easyocr.easyocr import Reader
from PIL.Image import Image as PILImage
from ultralytics.engine.results import Boxes

from utils.constants import OCR_BLOCKLIST
from utils.detections.preprocess_image import preprocess_image


def run_ocr(reader: Reader, image: PILImage, box: Boxes) -> str:
    x_min, y_min, x_max, y_max = cast(List[float], box.xyxy[0].tolist())  # type: ignore
    crop = image.crop((x_min, y_min, x_max, y_max))
    np_crop = np.array(crop)

    preprocessed = preprocess_image(np_crop)

    text = reader.readtext(  # type: ignore
        preprocessed,
        detail=0,
        paragraph=True,
        blocklist=OCR_BLOCKLIST,
    )

    return cast(str, text[-1])
