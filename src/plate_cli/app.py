from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rich.console import Group
from rich.spinner import Spinner
from rich.table import Table

from plate_cli.cli import CLI
from plate_cli.constants import ACCEPTED_IMAGE_FORMATS
from plate_cli.models import Models
from plate_cli.utils.draw_box import draw_box
from plate_cli.utils.menu import Menu


class App:
    def __init__(self) -> None:
        self.cli = CLI()
        self.models = Models()
        self.options = {
            "Cargar imágenes": self.process_path,
            "Detectar en tiempo real": self.run_camera,
            "Salir": self.exit,
        }
        self.__setup()

    def __setup(self):
        with self.cli.status(Spinner("dots", "[bold]Cargando modelo...")) as status:
            self.models.load_yolo()
            status.update(
                Group(
                    "[green]✓ Modelo cargado exitosamente",
                    Spinner("dots", text="[bold]Cargando OCR..."),
                )
            )
            self.models.load_reader()

    def run(self) -> None:
        menu = Menu(self.options)
        choice = menu.run()
        if choice in self.options:
            self.options[choice]()
        else:
            self.cli.error("La opción no existe")

    def process_path(self) -> None:
        prompt = self.cli.prompt("Seleccionar lote o imagen")
        path = prompt.ask()

        if path is None:
            return

        path = Path(path)

        if not path.exists():
            self.cli.error("La ruta no existe")
            return

        now = datetime.now()

        output_dir = Path(f"results/{now.strftime('%Y%m%d%H%M%S')}")

        if path.is_file():
            self.inference_from_file(path, output_dir)
        else:
            files = [
                f
                for f in path.iterdir()
                if f.is_file() and f.suffix in ACCEPTED_IMAGE_FORMATS
            ]
            if len(files) == 0:
                self.cli.error("No se han encontrado imágenes en la carpeta")
                return
            for file in files:
                self.inference_from_file(file, output_dir)

    def inference_from_file(self, path: Path, output_dir: Path):
        if path.suffix not in ACCEPTED_IMAGE_FORMATS:
            self.cli.error("Extensión no soportada")
            return

        image = Image.open(path)

        with self.cli.status(
            Spinner("dots", f"[bold]Detectando matrícula en {path.name}...")
        ) as status:
            result = self.models.inference(image)[0]

            if not result.boxes:
                self.cli.error("No se encontró ninguna matrícula")
                return

            status.update(
                Group(
                    "[green]✓ Matrícula detectada exitosamente",
                )
            )

        class_id = int(result.boxes[0].cls.item())
        class_name = result.names[class_id]
        text = self.models.get_text_from_image(image, result.boxes[0], class_name)

        image = Image.fromarray(draw_box(np.array(image), result, text))

        saved_image_path = self._save_image(image, class_name, text, output_dir)
        self.cli.success(
            f"[bold green]✓[/] Imagen guardada en: [cyan]{saved_image_path}"
        )

    def run_camera(self) -> None:
        capture = cv2.VideoCapture(0)
        if not capture.isOpened():
            self.cli.error("No se pudo abrir la cámara")
            return

        table = Table(title="Detección en tiempo real", show_header=True)
        table.add_column("País", style="cyan")
        table.add_column("Matrícula", style="magenta")
        table.add_column("Confianza", style="green")

        with self.cli.status(table, title="PlateCLI") as status:
            try:
                while True:
                    return_value, frame = capture.read()
                    if not return_value:
                        break

                    results = self.models.inference(frame, stream=True)

                    for result in results:
                        if result.boxes:
                            box = result.boxes[0]

                            # Convertir frame a imagen RGB y luego a imagen PIL para usarse en el OCR
                            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            pil_img = Image.fromarray(img_rgb)

                            conf = f"{box.conf.item():.2f}"
                            class_name = result.names[int(box.cls.item())]
                            text = self.models.get_text_from_image(
                                pil_img, box, class_name
                            )

                            draw_box(frame, result, text)

                            table.add_row(class_name, text, conf)
                            status.update(self.cli.build_panel(table, title="PlateCLI"))

                    cv2.imshow("Presiona 'q' para salir", frame)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break
            finally:
                capture.release()
                cv2.destroyAllWindows()

    def exit(self) -> None:
        self.cli.print("[bold]¡Que tenga un buen día! :waving_hand:[/]", width=40)

    def _save_image(
        self, image: Image.Image, class_name: str, text: str, output_dir: Path
    ) -> Path:
        filename = f"{class_name}_{text.replace(' ', '_')}.jpg"

        output_dir.mkdir(exist_ok=True, parents=True)

        save_path = output_dir / filename

        image.save(save_path)

        return save_path.resolve()
