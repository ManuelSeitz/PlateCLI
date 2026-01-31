from rich.console import Console

from plate_cli.app import App

console = Console()


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()
