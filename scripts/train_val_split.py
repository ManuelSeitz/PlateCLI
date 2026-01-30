import argparse
import random
import shutil
from glob import glob
from os import makedirs, path


def split_dataset(
    input_path: str, output_path: str = "data", train_percent: float = 0.9
):
    """Divide el dataset en entrenamiento y validación."""
    shutil.copytree(input_path, output_path, dirs_exist_ok=True)

    image_paths = glob(path.join(output_path, "images", "*.jpg"))
    total_train = round(len(image_paths) * train_percent)
    random.shuffle(image_paths)

    train_path = path.join(output_path, "train")
    val_path = path.join(output_path, "val")

    train_images = image_paths[:total_train]

    makedirs(train_path, exist_ok=True)
    makedirs(val_path, exist_ok=True)

    makedirs(path.join(train_path, "images"), exist_ok=True)

    makedirs(path.join(train_path, "labels"), exist_ok=True)

    for train_image in train_images:
        base = path.splitext(path.basename(train_image))[0]
        label_path = path.join(output_path, "labels", base + ".txt")

        shutil.move(train_image, path.join(train_path, "images"))
        shutil.move(label_path, path.join(train_path, "labels"))

    shutil.move(path.join(output_path, "images"), val_path)
    shutil.move(path.join(output_path, "labels"), val_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Divide un dataset en entrenamiento y validación"
    )
    parser.add_argument("--input-path", type=str, help="Ruta del dataset")
    parser.add_argument("--output-path", type=str, default="data")
    parser.add_argument(
        "--train-percent",
        type=float,
        default=0.9,
    )

    args = parser.parse_args()

    split_dataset(
        input_path=args.input_path,
        output_path=args.output_path,
        train_percent=args.train_percent,
    )
