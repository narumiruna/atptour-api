from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


def _to_atp_alias(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("_"))


class AtpModel(BaseModel):
    model_config = ConfigDict(alias_generator=_to_atp_alias, extra="allow", populate_by_name=True)


class Player(AtpModel):
    player_id: str | None
    player_country: str | None
    player_country_name: str | None
    player_first_name: str | None
    player_last_name: str | None


class SetScore(AtpModel):
    set_number: int
    set_score: int | None
    tie_break_score: int | None
    stats: Any | None


class MatchTeam(AtpModel):
    player: Player
    partner: Player
    entry_type: str | None
    seed: int | None
    game_score: str | None
    set_scores: list[SetScore]


class TeamTieResults(AtpModel):
    round_robin_group_number: int
    round_robin_group_name: str | None
    round_robin_city_name: str | None
    team_country_code: str | None
    team_country_name: str | None
    team_country_hemisphere_image_cms_url: str
    opponent_team_country_code: str | None
    opponent_team_country_name: str | None
    opponent_team_country_hemisphere_image_cms_url: str
    team_tie_match_wins: int
    opponent_team_tie_match_wins: int
    total_tie_matches_played: int
    tie_winner_team_country_code: str | None
    is_round_robin: bool
    player_team_countries_index: str


class LiveMatch(AtpModel):
    match_type: str = Field(alias="Type")
    team_tie_results: TeamTieResults
    match_id: str
    org: str
    is_doubles: bool
    round_name: str
    court_name: str
    court_id: int
    match_time_total: str
    match_state_reason_message: str | None
    extended_message: str | None
    has_challenger_tv_mobile: bool
    has_watch_live: bool
    has_head2_head: bool
    has_stats: bool
    has_court_tracking: bool
    match_status: str
    server_team: int
    winning_player_id: str | None
    umpire_first_name: str | None
    umpire_last_name: str | None
    last_updated: datetime
    k_seq: int
    rail_position: int | None
    live_listing_position: int | None
    player_team: MatchTeam
    opponent_team: MatchTeam


class LiveTeamTieDetail(AtpModel):
    team_tie_results: TeamTieResults
    matches: list[LiveMatch]


class Tournament(AtpModel):
    event_year: int
    event_id: int
    event_title: str
    event_country_code: str
    event_country: str
    event_location: str
    event_city: str
    event_start_date: str
    event_end_date: str
    has_team_tie_stats: bool
    event_type: str
    event_current_day_number: int
    sort_order_level: int
    tournament_position: int
    is_live: bool
    live_matches: list[LiveMatch]
    live_team_tie_details: list[LiveTeamTieDetail]
    draws_link: str
    schedule_link: str


class LiveMatchesData(AtpModel):
    event_year: int
    event_level: str
    live_matches_tournaments_ordered: list[Tournament]


class LiveMatchesResponse(AtpModel):
    content: Any | None
    data: LiveMatchesData
