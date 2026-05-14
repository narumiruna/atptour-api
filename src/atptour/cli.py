import time
from typing import Annotated

import typer
from rich.console import Console

from atptour.live import ScoringTournamentLevel
from atptour.live import fetch_live_matches
from atptour.live import render_live_matches

app = typer.Typer()
console = Console()


@app.command()
def main(
    level: Annotated[ScoringTournamentLevel, typer.Option(help="ATP scoring tournament level.")] = "tour",
    once: Annotated[bool, typer.Option(help="Fetch once and exit.")] = False,
) -> None:
    while True:
        response = fetch_live_matches(level)
        console.print(render_live_matches(response))
        console.print()

        if once:
            return

        time.sleep(15)


if __name__ == "__main__":
    app()
