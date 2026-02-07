from pathlib import Path
from typing import cast

import cv2
import numpy as np
from cv2.typing import MatLike
from numpy.typing import NDArray


def crop_image(image: NDArray[np.uint8], country: str) -> NDArray[np.uint8]:
    h, w = image.shape[:2]

    crops = {
        "argentina": image[int(h * 0.2) : h, 0:w],
        "bolivia": image[int(h * 0.2) : h, 0:w],
        "brazil": image[int(h * 0.25) : h, int(w * 0.05) : int(w * 0.95)],
        "chile": image[0 : int(h * 0.9), 0:w],
    }

    if country not in crops:
        return image[0:h, 0:w]

    return crops[country]


def preprocess_image(image: NDArray[np.uint8], country: str) -> NDArray[np.uint8]:
    image = crop_image(image, country)

    resized = cv2.resize(image, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=3)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)

    blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    kernel = np.ones((6, 6), np.uint8)

    # Eliminar puntos o líneas pequeñas
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    final_img = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel)

    # Descomentar para debug
    # save_preprocess(final_img, country)

    return cast(NDArray[np.uint8], final_img)


def save_preprocess(final_img: MatLike, country: str):
    output_path = Path(f"preprocess/{country}.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), final_img)
