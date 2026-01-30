from typing import Any, Dict

from rich.console import RenderableType
from rich.panel import Panel


def get_panel(renderable: RenderableType, **kwargs: Any) -> Panel:
    options: Dict[str, Any] = {
        "title": "[bold cyan]PlateCLI",
        "border_style": "bright_blue",
        "padding": (1, 2),
    }
    options.update(kwargs)

    return Panel(renderable, **options)
