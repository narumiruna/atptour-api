import logging
import time
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from atptour.live import ScoringTournamentLevel
from atptour.live import fetch_live_matches
from atptour.live import render_live_matches

app = typer.Typer()
console = Console()
logger = logging.getLogger(__name__)

DEFAULT_LOG_FILE = Path("logs/atptour.log")


def configure_logging(log_file: Path = DEFAULT_LOG_FILE) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=log_file,
        format="%(asctime)s | %(levelname)s | %(name)s:%(lineno)d - %(message)s",
        level=logging.INFO,
        force=True,
    )


@app.command()
def main(
    level: Annotated[ScoringTournamentLevel, typer.Option(help="ATP scoring tournament level.")] = "tour",
    once: Annotated[bool, typer.Option(help="Fetch once and exit.")] = False,
) -> None:
    configure_logging()
    consecutive_errors = 0

    while True:
        try:
            response = fetch_live_matches(level)
        except Exception:
            consecutive_errors += 1
            logger.exception("Failed to fetch live matches level=%s consecutive_errors=%s", level, consecutive_errors)
            console.print(f"[red]Failed to fetch live matches. Logged to {DEFAULT_LOG_FILE}.[/red]")
        else:
            consecutive_errors = 0
            console.print(render_live_matches(response))
            console.print()

        if once:
            return

        time.sleep(15)


if __name__ == "__main__":
    app()
