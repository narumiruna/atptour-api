import json
from pathlib import Path

from atptour.models import LiveMatchesResponse

DATA_DIR = Path(__file__).parent / "data"


def test_parse_live_matches_samples() -> None:
    for path in [DATA_DIR / "livematches_tour.json", DATA_DIR / "livematches_challenger.json"]:
        payload = json.loads(path.read_text())

        response = LiveMatchesResponse.model_validate(payload)

        assert response.content is None
        assert response.data.event_level in {"tour", "challenger"}
        assert response.data.live_matches_tournaments_ordered


def test_parse_sample_live_match_details() -> None:
    payload = json.loads((DATA_DIR / "livematches_tour.json").read_text())

    response = LiveMatchesResponse.model_validate(payload)
    tournament = response.data.live_matches_tournaments_ordered[0]
    match = tournament.live_matches[0]

    assert tournament.event_title == "Internazionali BNL d'Italia"
    assert match.match_type == "singles"
    assert match.player_team.player.player_id == "S0AG"
    assert match.opponent_team.player.player_id == "RE44"
    assert match.player_team.set_scores[0].set_number == 1
