from rich.console import Console

from utils.error import show_error
from utils.menu import OPTIONS, Menu

console = Console()

if __name__ == "__main__":
    menu = Menu()
    choice = menu.run()
    if choice in OPTIONS:
        OPTIONS[choice]()
    else:
        show_error(":x: La opción no existe")
