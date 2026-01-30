from rich.console import Console

from plate_cli.utils.panel import get_panel


def exit_app():
    console = Console()
    panel = get_panel("[bold]¡Que tenga un buen día! :waving_hand:[/]", width=40)
    console.print(panel)
