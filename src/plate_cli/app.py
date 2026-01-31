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
            self.cli.error(":x: La opción no existe")

    def process_path(self) -> None:
        prompt = self.cli.prompt("Seleccionar lote o imagen")
        path = prompt.ask()

        if path is None:
            return

        path = Path(path)

        if not path.exists():
            self.cli.error(":x: La ruta no existe")
            return

        if path.is_file():
            self.inference_from_file(path)

    def inference_from_file(self, path: Path):
        if path.suffix not in ACCEPTED_IMAGE_FORMATS:
            self.cli.error(":x: Extensión no soportada")
            return

        image = Image.open(path)

        with self.cli.status(
            Spinner("dots", "[bold]Detectando matrícula...")
        ) as status:
            result = self.models.inference(image)[0]

            if not result.boxes:
                self.cli.error(":x: No se encontró ninguna matrícula")
                return

            status.update(
                Group(
                    "[green]✓ Matrícula detectada exitosamente",
                )
            )

        text = self.models.get_text_from_image(image, result.boxes[0])
        class_id = int(result.boxes[0].cls.item())
        class_name = result.names[class_id]

        image = Image.fromarray(draw_box(np.array(image), result, text))

        saved_image_path = self._save_image(image, class_name, text)
        self.cli.success(
            f"[bold green]✓[/] Imagen guardada en: [cyan]{saved_image_path}"
        )

    def run_camera(self) -> None:
        capture = cv2.VideoCapture(0)
        if not capture.isOpened():
            self.cli.error(":x: No se pudo abrir la cámara")
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

                    results = self.models.inference(frame)

                    for result in results:
                        if result.boxes:
                            box = result.boxes[0]

                            # Convertir frame a imagen RGB y luego a imagen PIL para usarse en el OCR
                            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            pil_img = Image.fromarray(img_rgb)

                            text = self.models.get_text_from_image(pil_img, box)

                            draw_box(frame, result, text)

                            conf = f"{box.conf.item():.2f}"
                            class_name = result.names[int(box.cls.item())]
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

    def _save_image(self, image: Image.Image, class_name: str, text: str) -> Path:
        filename = f"{class_name}_{text.replace(' ', '_')}.jpg"

        output_dir = Path("results")
        output_dir.mkdir(exist_ok=True)

        save_path = output_dir / filename

        image.save(save_path)

        return save_path.resolve()
