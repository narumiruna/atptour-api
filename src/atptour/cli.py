import logging
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Annotated
from typing import Literal

import typer
from curl_cffi import requests
from rich.console import Console

from atptour.live import DEFAULT_TIMEOUT_SECONDS
from atptour.live import ScoringTournamentLevel
from atptour.live import fetch_live_matches
from atptour.live import render_live_matches

app = typer.Typer()
console = Console()
logger = logging.getLogger(__name__)

DEFAULT_LOG_FILE = Path("logs/atptour.log")
DEFAULT_INTERVAL_SECONDS = 15.0
DEFAULT_LOG_MAX_BYTES = 5 * 1024 * 1024
DEFAULT_LOG_BACKUP_COUNT = 5

CliScoringTournamentLevel = Literal["tour", "challenger", "all"]


def configure_logging(
    log_file: Path = DEFAULT_LOG_FILE,
    *,
    max_bytes: int = DEFAULT_LOG_MAX_BYTES,
    backup_count: int = DEFAULT_LOG_BACKUP_COUNT,
) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s:%(lineno)d - %(message)s"))

    logging.basicConfig(
        handlers=[handler],
        level=logging.INFO,
        force=True,
    )


def _levels(level: CliScoringTournamentLevel) -> tuple[ScoringTournamentLevel, ...]:
    if level == "all":
        return ("tour", "challenger")
    return (level,)


def _format_now() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def _response_status_code(exc: Exception) -> int | None:
    response = getattr(exc, "response", None)
    return getattr(response, "status_code", None)


def _response_text_snippet(exc: Exception, limit: int = 500) -> str | None:
    response = getattr(exc, "response", None)
    text = getattr(response, "text", None)
    if text is None:
        return None
    return " ".join(str(text).split())[:limit]


def _log_fetch_failure(
    *,
    exc: Exception,
    level: ScoringTournamentLevel,
    consecutive_errors: int,
    timeout: float,
) -> None:
    logger.exception(
        "Failed to fetch live matches level=%s consecutive_errors=%s status_code=%s timeout=%s response_text=%r",
        level,
        consecutive_errors,
        _response_status_code(exc),
        timeout,
        _response_text_snippet(exc),
    )


@app.command()
def main(
    level: Annotated[CliScoringTournamentLevel, typer.Option(help="ATP scoring tournament level.")] = "tour",
    once: Annotated[bool, typer.Option(help="Fetch once and exit.")] = False,
    interval: Annotated[
        float,
        typer.Option(min=1.0, help="Seconds to wait between fetches when watching."),
    ] = DEFAULT_INTERVAL_SECONDS,
    log_file: Annotated[Path, typer.Option(help="File path for fetch failure logs.")] = DEFAULT_LOG_FILE,
    timeout: Annotated[
        float,
        typer.Option(min=1.0, help="HTTP request timeout in seconds."),
    ] = DEFAULT_TIMEOUT_SECONDS,
) -> None:
    configure_logging(log_file)
    consecutive_errors = 0

    while True:
        had_error = False
        for scoring_level in _levels(level):
            try:
                response = fetch_live_matches(scoring_level, timeout=timeout)
            except (requests.RequestsError, ValueError) as exc:
                had_error = True
                consecutive_errors += 1
                _log_fetch_failure(
                    exc=exc,
                    level=scoring_level,
                    consecutive_errors=consecutive_errors,
                    timeout=timeout,
                )
                retry_message = "" if once else f" Retrying in {interval:g} seconds."
                console.print(
                    f"[{_format_now()}] [red]Failed to fetch {scoring_level} live matches. "
                    f"Logged to {log_file}.{retry_message}[/red]"
                )
            else:
                consecutive_errors = 0
                console.print(render_live_matches(response))
                console.print()

        if had_error:
            console.print()

        if once:
            return

        time.sleep(interval)


if __name__ == "__main__":
    app()
