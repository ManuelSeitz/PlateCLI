import argparse
from os import path
from typing import Any

import yaml


def generate_dataset_yaml(data_path: str = "data"):
    """Genera un archivo de configuración YAML para un dataset YOLO."""
    train_path = path.join(data_path, "train")
    val_path = path.join(data_path, "val")
    lines: list[str] = []

    with open(path.join(data_path, "classes.txt"), "r", encoding="utf-8") as f:
        lines = f.readlines()

    classes: dict[int, str] = {}

    for index, line in enumerate(lines):
        classes[index] = line.rstrip("\n")

    data: dict[str, Any] = {
        # "path": data_path,
        "train": train_path,
        "val": val_path,
        "nc": len(lines),
        "names": classes,
    }

    with open("data.yaml", "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Genera un archivo de configuración YAML"
    )
    parser.add_argument(
        "--data-path", type=str, default="data", help="Ruta del dataset"
    )

    args = parser.parse_args()

    generate_dataset_yaml(data_path=args.data_path)
