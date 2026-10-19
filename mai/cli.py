import argparse
import sys

from rich.console import Console
from rich.markup import escape
from rich.progress import track as progress
from rich.prompt import Confirm, Prompt
from rich.table import Table

from mai import tidal, youtube
from mai.parser import parse_tracklist

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


def show_login_link(url: str, expires_in: int) -> None:
    console.print("\n[bold]Log in to Tidal[/] (opening your browser):")
    console.print(f"  [cyan underline]{url}[/]")
    console.print(f"  [dim]Waiting for approval… the link expires in {expires_in // 60} min.[/]")


def matches_table(matches: list[tidal.Match]) -> Table:
    table = Table(show_lines=False, header_style="bold magenta")
    table.add_column("#", justify="right", style="dim")
    table.add_column("From the description")
    table.add_column("On Tidal")
    table.add_column("Score", justify="right")
    for i, m in enumerate(matches, 1):
        color = "green" if m.score >= tidal.SURE else "yellow" if m.item else "red"
        found = escape(m.label) if m.item else "not found"
        if m.query.kind == "album":
            found = f"[dim](album)[/] {found}"
        table.add_row(str(i), escape(m.query.query), f"[{color}]{found}[/]", f"[{color}]{m.score:.0%}[/]")
    return table


def review(matches: list[tidal.Match]) -> list[tidal.Match]:
    """Return the matches the user wants in the playlist."""
    sure = [m for m in matches if m.item and m.score >= tidal.SURE]
    doubtful = [m for m in matches if m.item and m.score < tidal.SURE]
    if not doubtful:
        return sure

    console.print(f"\n[yellow]{len(doubtful)}[/] match(es) look doubtful.")
    choice = Prompt.ask(
        "Keep them? [bold]a[/]ll / [bold]r[/]eview one by one / [bold]n[/]one",
        choices=["a", "r", "n"],
        default="r",
    )
    if choice == "a":
        kept = doubtful
    elif choice == "n":
        kept = []
    else:
        kept = [
            m
            for m in doubtful
            if Confirm.ask(f"  {escape(m.query.query)} [dim]→[/] [yellow]{escape(m.label)}[/]?", default=False)
        ]
    # Keep the original order of the description.
    return [m for m in matches if m in sure or m in kept]


def run(url: str | None) -> int:
    url = url or Prompt.ask("[bold]YouTube link[/]").strip()

    with console.status("Reading the video…"):
        video = youtube.fetch_video(url)
    console.print(f"[bold]🎬 {escape(video.title)}[/]")

    queries = parse_tracklist(video.description)
    if not queries:
        console.print("[red]No tracklist found in the description.[/]")
        return 1
    console.print(f"Found [bold]{len(queries)}[/] songs/albums in the description.")

    session = tidal.login(show_login_link)
    console.print("[green]✓[/] Logged in to Tidal")

    matches = [tidal.find_match(session, q) for q in progress(queries, description="Searching Tidal…", console=console)]
    console.print(matches_table(matches))

    chosen = review(matches)
    missing = [m for m in matches if m.item is None]
    if not chosen:
        console.print("[red]Nothing to add, no playlist created.[/]")
        return 1

    name = Prompt.ask("\n[bold]Playlist name[/]", default=video.title)
    if not Confirm.ask(f"Create [bold]{escape(name)}[/] with {len(chosen)} item(s)?", default=True):
        return 1

    with console.status("Creating the playlist…"):
        ids = tidal.track_ids(chosen)
        playlist = tidal.create_playlist(session, name, f"From {url} · {FOOTER}", ids)
        cover = youtube.download_thumbnail(video)

    console.print(f"\n[green]✓ Playlist created[/] with {len(ids)} tracks: [cyan underline]{playlist.share_url}[/]")
    if cover:
        console.print(f"[dim]Cover saved to[/] {escape(str(cover.resolve()))}")
    skipped = len(matches) - len(chosen) - len(missing)
    if skipped:
        console.print(f"[yellow]{skipped} discarded[/]")
    if missing:
        console.print(f"[red]{len(missing)} not found on Tidal:[/]")
        for m in missing:
            console.print(f"  [dim]·[/] {escape(m.query.raw)}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="mai",
        description="Turn a YouTube video's tracklist into a Tidal playlist.",
        epilog=FOOTER,
    )
    parser.add_argument("url", nargs="?", help="YouTube video URL")
    args = parser.parse_args()

    print_banner()
    try:
        code = run(args.url)
    except KeyboardInterrupt:
        console.print("\n[dim]Bye![/]")
        code = 130
    except Exception as e:  # show a friendly error instead of a traceback
        console.print(f"\n[red]Error:[/] {escape(str(e))}")
        code = 1
    print_footer()
    sys.exit(code)
