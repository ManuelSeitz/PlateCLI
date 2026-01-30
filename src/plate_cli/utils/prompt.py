import io
from typing import Optional

from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from rich.console import Console
from rich.panel import Panel


class Prompt:
    def __init__(self, title: str):
        self.title = title
        self.buffer = io.StringIO()
        self.console = Console(
            file=self.buffer, force_terminal=True, color_system="truecolor"
        )

        # Lógica de entrada con autocompletado de archivos
        self.path_buffer = Buffer(completer=PathCompleter(expanduser=True))

        self.kb = self._setup_key_bindings()
        self.app = self._setup_app()

    def _setup_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()

        @kb.add("enter")
        def _(event: KeyPressEvent):
            # Retorna el texto escrito en el buffer de entrada
            event.app.exit(result=self.path_buffer.text)

        # Control + C
        @kb.add("c-c")
        def _(event: KeyPressEvent):
            event.app.exit()

        return kb

    def _get_header_rendered(self) -> ANSI:
        self.buffer.truncate(0)
        self.buffer.seek(0)

        panel = Panel(
            "[bold white]Ingrese la ruta del archivo/carpeta[/]\n"
            "[gray]Use TAB para autocompletar[/]",
            title=f"[bold cyan]{self.title}",
            border_style="bright_blue",
            padding=(1, 2),
            width=60,
        )

        self.console.print(panel)
        return ANSI(self.buffer.getvalue())

    def _setup_app(self) -> Application[str]:
        # Parte superior
        header_window = Window(
            content=FormattedTextControl(self._get_header_rendered),
            height=5,
        )

        # Parte inferior
        input_field = Window(
            content=BufferControl(buffer=self.path_buffer), height=1, left_margins=[]
        )

        # Contenedor para el input
        input_line = VSplit(
            [Window(FormattedTextControl([("fg:cyan", " ➜ ")]), width=4), input_field]
        )

        root_container = HSplit(
            [
                header_window,
                input_line,
                Window(height=1),  # Espacio extra al final
            ]
        )

        return Application(
            layout=Layout(root_container),
            key_bindings=self.kb,
            full_screen=True,
        )

    def ask(self) -> Optional[str]:
        return self.app.run()
