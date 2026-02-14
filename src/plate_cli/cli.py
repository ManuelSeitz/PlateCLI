from contextlib import contextmanager
from typing import Any, Dict, Generator

from rich.console import Console, RenderableType
from rich.live import Live
from rich.panel import Panel
from rich.spinner import Spinner
from rich.text import Text

from plate_cli.utils.prompt import Prompt


class CLI:
    def __init__(self) -> None:
        self.console = Console()

    def print(self, renderable: RenderableType, **kwargs: Any):
        panel = self.build_panel(renderable, **kwargs)
        self.console.print(panel)

    def prompt(self, title: str) -> Prompt:
        return Prompt(title)

    @contextmanager
    def status(
        self, initial_renderable: RenderableType = Spinner("dots"), **kwargs: Any
    ) -> Generator["StatusHandler", None, None]:
        options: Dict[str, Any] = {"width": 60, "expand": False}
        options.update(kwargs)

        handler = StatusHandler(self, initial_renderable, options)

        with Live(
            handler.get_panel(),
            console=self.console,
            refresh_per_second=10,
            screen=False,
            transient=True,
        ) as live:
            handler.set_live(live)
            yield handler

    def error(self, renderable: RenderableType, **kwargs: Any) -> None:
        panel = self.build_panel(
            Text.from_markup(":x: ") + renderable,
            title="[bold red]PlateCLI",
            border_style="red",
            padding=(1, 4, 1, 2),
            expand=False,
            **kwargs,
        )
        self.console.print(panel)

    def success(self, renderable: RenderableType, **kwargs: Any) -> None:
        options: Dict[str, Any] = {"border_style": "green", "expand": False}
        options.update(kwargs)

        self.console.print(Panel(renderable, **options))

    def build_panel(self, renderable: RenderableType, **kwargs: Any) -> Panel:
        options: Dict[str, Any] = {
            "title": "[bold cyan]PlateCLI",
            "border_style": "bright_blue",
            "padding": (1, 8, 1, 2),
        }
        options.update(kwargs)

        return Panel(renderable, **options)


class StatusHandler:
    def __init__(
        self, cli_instance: CLI, renderable: RenderableType, options: Dict[str, Any]
    ):
        self.cli = cli_instance
        self.renderable = renderable
        self.options = options
        self.live: Live | None = None

    def set_live(self, live: Live):
        self.live = live

    def get_panel(self) -> Panel:
        return self.cli.build_panel(self.renderable, **self.options)

    def update(self, renderable: RenderableType, **new_options: Any):
        self.renderable = renderable

        if isinstance(renderable, Panel):
            self.renderable = renderable.renderable
        else:
            self.renderable = renderable

        self.options.update(new_options)
        if self.live:
            self.live.update(self.get_panel())
