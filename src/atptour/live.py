from __future__ import annotations

from datetime import datetime
from typing import Literal

from curl_cffi import requests
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from atptour.models import LiveMatch
from atptour.models import LiveMatchesResponse
from atptour.models import MatchTeam
from atptour.models import Tournament

ScoringTournamentLevel = Literal["tour", "challenger"]

LIVE_MATCHES_URL = "https://app.atptour.com/api/v2/gateway/livematches/website"
DEFAULT_TIMEOUT_SECONDS = 30.0

_session: requests.Session | None = None


def get_session() -> requests.Session:
    global _session
    if _session is None:
        _session = requests.Session()
    return _session


def fetch_live_matches(
    level: ScoringTournamentLevel = "tour",
    *,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    session: requests.Session | None = None,
) -> LiveMatchesResponse:
    client = session or get_session()
    response = client.get(
        LIVE_MATCHES_URL,
        params={"scoringTournamentLevel": level},
        impersonate="chrome",
        headers={
            "accept": "application/json, text/plain, */*",
            "origin": "https://www.atptour.com",
            "referer": "https://www.atptour.com/",
        },
        timeout=timeout,
    )
    response.raise_for_status()
    return LiveMatchesResponse.model_validate(response.json())


def format_live_matches(response: LiveMatchesResponse) -> str:
    captured_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    lines = [f"[{captured_at}] ATP {response.data.event_level} live matches"]

    for tournament in response.data.live_matches_tournaments_ordered:
        lines.extend(_format_tournament(tournament))

    return "\n".join(lines)


def render_live_matches(response: LiveMatchesResponse) -> Group:
    captured_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    title = f"ATP {response.data.event_level.title()} Live Matches"
    tables = [_render_tournament(tournament) for tournament in response.data.live_matches_tournaments_ordered]
    return Group(Panel(Text(captured_at, style="dim"), title=title, border_style="cyan"), *tables)


def _render_tournament(tournament: Tournament) -> Panel:
    table = Table(expand=True, show_header=True, header_style="bold cyan")
    table.add_column("Match")
    table.add_column("Score", no_wrap=True)
    table.add_column("Status", no_wrap=True)

    if not tournament.live_matches:
        table.add_row("No live matches", "-", "-")
    else:
        for match in tournament.live_matches:
            table.add_row(
                _render_match_summary(match),
                _format_score(match),
                _format_match_status(match.match_status),
            )

    subtitle = f"{tournament.event_city}, {tournament.event_country}"
    return Panel(table, title=tournament.event_title, subtitle=subtitle, border_style="blue")


def _render_match_summary(match: LiveMatch) -> Text:
    summary = Text()
    summary.append(f"{_format_team(match.player_team)} vs {_format_team(match.opponent_team)}", style="bold")
    summary.append(f"\n{match.round_name} · {match.court_name}", style="dim")
    if match.extended_message:
        summary.append(f"\n{match.extended_message}", style="yellow")
    return summary


def _format_tournament(tournament: Tournament) -> list[str]:
    matches = tournament.live_matches
    heading = f"{tournament.event_title} ({tournament.event_city}, {tournament.event_country})"

    if not matches:
        return ["", heading, "  No live matches."]

    lines = ["", heading]
    lines.extend(_format_match(match) for match in matches)
    return lines


def _format_match(match: LiveMatch) -> str:
    player = _format_team(match.player_team)
    opponent = _format_team(match.opponent_team)
    score = _format_score(match)
    court = f" | {match.court_name}" if match.court_name else ""
    message = f" | {match.extended_message}" if match.extended_message else ""

    return f"  {match.round_name} | {match.match_status}{court} | {player} vs {opponent} | {score}{message}"


def _format_match_status(status: str) -> str:
    labels = {
        "C": "Called",
        "F": "Final",
        "P": "Playing",
        "S": "Suspended",
        "W": "Warmup",
    }
    return labels.get(status, status)


def _format_team(team: MatchTeam) -> str:
    player = team.player
    name = " ".join(part for part in [player.player_first_name, player.player_last_name] if part)
    seed = f" ({team.seed})" if team.seed is not None else ""
    return f"{name or player.player_id or 'Unknown'}{seed}"


def _format_score(match: LiveMatch) -> str:
    player_scores = _format_set_scores(match.player_team)
    opponent_scores = _format_set_scores(match.opponent_team)
    player_game = match.player_team.game_score or "-"
    opponent_game = match.opponent_team.game_score or "-"

    return f"{player_scores} {player_game} - {opponent_scores} {opponent_game}"


def _format_set_scores(team: MatchTeam) -> str:
    scores = []
    for set_score in team.set_scores:
        if set_score.set_score is None:
            continue
        if set_score.tie_break_score is None:
            scores.append(str(set_score.set_score))
        else:
            scores.append(f"{set_score.set_score}({set_score.tie_break_score})")
    return " ".join(scores) if scores else "-"
