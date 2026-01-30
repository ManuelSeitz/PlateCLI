import io
from typing import Callable, Dict, List, Optional

from prompt_toolkit import Application
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from rich.console import Console

from plate_cli.features.camera import open_camera
from plate_cli.features.exit import exit_app
from plate_cli.features.load_images import load_images
from plate_cli.utils.panel import get_panel

OPTIONS: Dict[str, Callable[[], None]] = {
    "Cargar imágenes": load_images,
    "Detectar en tiempo real": open_camera,
    "Salir": exit_app,
}


class Menu:
    def __init__(self):
        self.options = list(OPTIONS.keys())
        self.selected_index = 0

        self.buffer = io.StringIO()
        self.console = Console(
            file=self.buffer, force_terminal=True, color_system="truecolor"
        )

        self.kb = self._setup_key_bindings()
        self.app = self._setup_app()

    def _setup_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()

        @kb.add("up")
        def _(event: KeyPressEvent):
            self.selected_index = (self.selected_index - 1) % len(self.options)

        @kb.add("down")
        def _(event: KeyPressEvent):
            self.selected_index = (self.selected_index + 1) % len(self.options)

        @kb.add("enter")
        def _(event: KeyPressEvent):
            event.app.exit(result=self.options[self.selected_index])

        # Control + C
        @kb.add("c-c")
        def _(event: KeyPressEvent):
            event.app.exit()

        return kb

    def _get_rendered_panel(self) -> ANSI:
        """Genera la representación visual del menú usando Rich."""
        # Limpiar buffer
        self.buffer.truncate(0)
        self.buffer.seek(0)

        menu_items: List[str] = []
        for i, option in enumerate(self.options):
            if i == self.selected_index:
                menu_items.append(f"[cyan]> {option}[/cyan]")
            else:
                menu_items.append(f"  {option}")

        content = "\n".join(menu_items)
        panel = get_panel(
            content,
            subtitle="Usa ⬆⬇ y Enter",
            width=40,
        )

        self.console.print(panel)
        return ANSI(self.buffer.getvalue())

    def _setup_app(self) -> Application[str]:
        body = Window(
            content=FormattedTextControl(self._get_rendered_panel),
            always_hide_cursor=True,
        )

        return Application(
            layout=Layout(HSplit([body])),
            key_bindings=self.kb,
            full_screen=True,
            refresh_interval=0.1,
        )

    def run(self) -> Optional[str]:
        """Inicia la aplicación y devuelve la opción seleccionada."""
        return self.app.run()
