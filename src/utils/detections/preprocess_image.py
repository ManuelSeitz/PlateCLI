from typing import cast

import cv2
import numpy as np
from numpy.typing import NDArray


def preprocess_image(image: NDArray[np.uint8]) -> NDArray[np.uint8]:
    h, w = image.shape[:2]
    image = image[int(h * 0.25) : int(h * 0.95), 0:w]

    resized = cv2.resize(image, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=3)

    clahe = cv2.createCLAHE(clipLimit=1.2, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)

    blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
    otsu_val, _ = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    _, final_img = cv2.threshold(blurred, otsu_val * 1.15, 255, cv2.THRESH_BINARY)

    return cast(NDArray[np.uint8], final_img)
