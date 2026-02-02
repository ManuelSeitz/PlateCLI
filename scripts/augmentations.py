import argparse
import os
import random
from collections import Counter
from typing import Dict, List

import albumentations as A
import cv2
import numpy as np

transform = A.Compose(
    [
        A.HorizontalFlip(p=0.5),
        A.RandomBrightnessContrast(p=0.2),
        A.Rotate(limit=20, p=0.5),
        A.RGBShift(p=0.2),
    ],
    bbox_params=A.BboxParams(format="yolo", label_fields=["class_labels"]),
)


def get_class_distribution(label_dir: str):
    """Cuenta la cantidad de instancias existentes de cada clase."""
    counts: Counter[int] = Counter()
    # Clases que contiene cada imagen
    image_classes: Dict[str, List[int]] = {}

    for label_file in os.listdir(label_dir):
        if not label_file.endswith(".txt"):
            continue

        file_id = os.path.splitext(label_file)[0]
        path = os.path.join(label_dir, label_file)

        with open(path, "r") as f:
            classes_in_file: List[int] = []
            for line in f:
                parts = line.split()
                if not parts:
                    continue
                cls = int(float(parts[0]))
                counts[cls] += 1
                classes_in_file.append(cls)
            image_classes[file_id] = classes_in_file

    return counts, image_classes


def augment_image(image_path: str, label_path: str, suffix: str):
    img_dir = os.path.dirname(image_path)
    label_dir = os.path.dirname(label_path)
    base_name = os.path.basename(image_path)
    file_name = os.path.splitext(base_name)[0]

    image = cv2.imread(image_path)
    if image is None:
        return
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    bboxes: List[List[float]] = []
    class_labels: List[int] = []

    if os.path.exists(label_path):
        with open(label_path, "r") as f:
            # Recorre cada línea porque puede haber más de una matrícula detectada
            for line in f:
                parts = line.split()
                # ID de clase + X Y w h
                if len(parts) == 5:
                    class_labels.append(int(float(parts[0])))
                    bboxes.append([float(x) for x in parts[1:]])

    transformed = transform(image=image, bboxes=bboxes, class_labels=class_labels)
    transformed_image = np.array(transformed["image"])
    transformed_bboxes = transformed["bboxes"]
    transformed_labels = transformed["class_labels"]

    new_file_name = f"{file_name}_{suffix}"

    # Guardar imagen
    cv2.imwrite(
        os.path.join(img_dir, f"{new_file_name}.jpg"),
        cv2.cvtColor(transformed_image, cv2.COLOR_RGB2BGR),
    )

    # Guardar label
    with open(os.path.join(label_dir, f"{new_file_name}.txt"), "w") as f:
        for cls, bbox in zip(transformed_labels, transformed_bboxes):
            bbox_str = " ".join(map(str, bbox))
            f.write(f"{cls} {bbox_str}\n")


def augmentation(image_dir: str, label_dir: str):
    counts, image_classes = get_class_distribution(label_dir)
    if not counts:
        print("No se encontraron etiquetas.")
        return

    max_samples = max(counts.values())
    print(f"Objetivo de muestras por clase: {max_samples}")

    # Mapear qué imágenes contienen cada clase
    class_images: Dict[int, List[str]] = {cls: [] for cls in counts.keys()}
    for file_id, classes in image_classes.items():
        for cls in set(classes):
            class_images[cls].append(file_id)

    # Balancear cada clase
    for cls, current_count in counts.items():
        needed = max_samples - current_count
        if needed <= 0:
            continue

        print(f"Aumentando clase {cls}: generando {needed} muestras nuevas...")

        images = class_images[cls]
        for i in range(needed):
            file_id = random.choice(images)

            img_path = os.path.join(image_dir, f"{file_id}.jpg")
            lbl_path = os.path.join(label_dir, f"{file_id}.txt")

            # Generar el aumento
            augment_image(img_path, lbl_path, suffix=f"aug_{i}")

    print("Balanceo completado con éxito.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Balanceador de clases YOLO usando Albumentations"
    )

    parser.add_argument(
        "--images", type=str, help="Ruta a la carpeta de imágenes (.jpg)"
    )
    parser.add_argument(
        "--labels",
        type=str,
        help="Ruta a la carpeta de etiquetas (.txt)",
    )

    args = parser.parse_args()

    if not os.path.exists(args.images) or not os.path.exists(args.labels):
        raise NotADirectoryError("Una de las rutas especificadas no existe.")

    print("Iniciando proceso de aumento...")
    augmentation(args.images, args.labels)
