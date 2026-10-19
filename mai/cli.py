import argparse

from rich.console import Console

console = Console()

BANNER = r"""
 ███╗   ███╗  █████╗  ██╗
 ████╗ ████║ ██╔══██╗ ██║
 ██╔████╔██║ ███████║ ██║
 ██║╚██╔╝██║ ██╔══██║ ██║
 ██║ ╚═╝ ██║ ██║  ██║ ██║
 ╚═╝     ╚═╝ ╚═╝  ╚═╝ ╚═╝
"""

FOOTER = "made with love @jakedogguy"


def print_banner() -> None:
    console.print(BANNER, style="bold magenta", highlight=False)
    console.print("  YouTube tracklist → Tidal playlist\n", style="dim")


def print_footer() -> None:
    console.print(f"\n[magenta]♥[/] [dim]{FOOTER}[/]")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="mai",
        description="Turn a YouTube video's tracklist into a Tidal playlist.",
        epilog=FOOTER,
    )
    parser.add_argument("url", nargs="?", help="YouTube video URL")
    parser.parse_args()

    print_banner()
    print_footer()
