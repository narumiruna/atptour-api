import json
from pathlib import Path

from rich.console import Console

from atptour.live import format_live_matches
from atptour.live import render_live_matches
from atptour.models import LiveMatchesResponse

DATA_DIR = Path(__file__).parent / "data"


def test_format_live_matches() -> None:
    payload = json.loads((DATA_DIR / "livematches_tour.json").read_text())
    response = LiveMatchesResponse.model_validate(payload)

    output = format_live_matches(response)

    assert "ATP tour live matches" in output
    assert "Internazionali BNL d'Italia" in output
    assert "Jannik Sinner (1) vs Andrey Rublev (12)" in output


def test_render_live_matches() -> None:
    payload = json.loads((DATA_DIR / "livematches_tour.json").read_text())
    response = LiveMatchesResponse.model_validate(payload)
    console = Console(record=True, width=120)

    console.print(render_live_matches(response))
    output = console.export_text()

    assert "ATP Tour Live Matches" in output
    assert "Internazionali BNL d'Italia" in output
    assert "Jannik Sinner (1) vs Andrey" in output
    assert "Rublev (12)" in output
