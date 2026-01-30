from rich.console import Console

from plate_cli.utils.error import show_error
from plate_cli.utils.menu import OPTIONS, Menu

console = Console()


def main():
    menu = Menu()
    choice = menu.run()
    if choice in OPTIONS:
        OPTIONS[choice]()
    else:
        show_error(":x: La opción no existe")


if __name__ == "__main__":
    main()
