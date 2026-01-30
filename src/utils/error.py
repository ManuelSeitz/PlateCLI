from typing import Any

from rich.console import Console, RenderableType

from utils.panel import get_panel


def show_error(renderable: RenderableType, **kwargs: Any):
    console = Console()
    panel = get_panel(
        renderable, title="[bold red]PlateCLI", border_style="red", width=40, **kwargs
    )
    console.print(panel)
