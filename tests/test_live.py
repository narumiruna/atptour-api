import json
from pathlib import Path
from typing import cast

from curl_cffi import requests
from rich.console import Console

from atptour.live import fetch_live_matches
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


def test_fetch_live_matches_uses_shared_request_shape() -> None:
    payload = json.loads((DATA_DIR / "livematches_tour.json").read_text())
    calls = []

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self):
            return payload

    class FakeSession:
        def get(self, *args, **kwargs):
            calls.append((args, kwargs))
            return FakeResponse()

    response = fetch_live_matches("tour", timeout=7, session=cast(requests.Session, FakeSession()))

    assert response.data.event_level == "tour"
    assert calls[0][1]["params"] == {"scoringTournamentLevel": "tour"}
    assert calls[0][1]["impersonate"] == "chrome"
    assert calls[0][1]["timeout"] == 7
