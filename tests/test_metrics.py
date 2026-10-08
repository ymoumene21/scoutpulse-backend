from datetime import date

import polars as pl
import pytest

from processing.metrics import rolling_avg_rating, player_event_counts, team_form


def make_events_df():
    """Tiny hand-made stand-in for fetch_events_df(): same column names, no database."""
    return pl.DataFrame({
        "player_id":   [1, 1, 1, 1, 2],
        "match_date":  [date(2024, 1, 1), date(2024, 1, 8), date(2024, 1, 15), date(2024, 1, 15), date(2024, 1, 1)],
        "event_type":  ["rating", "rating", "rating", "goal", "rating"],
        "event_value": [6.0, 7.0, 9.0, None, 5.0],
    })


def test_rolling_avg_uses_last_n_ratings():
    df = make_events_df()
    # last 2 ratings for player 1 are 7.0 and 9.0 -> 8.0 (the older 6.0 must be ignored)
    assert rolling_avg_rating(df, player_id=1, window=2) == 8.0


def test_rolling_avg_returns_none_for_player_with_no_ratings():
    df = make_events_df()
    assert rolling_avg_rating(df, player_id=999, window=5) is None


def test_player_event_counts():
    df = make_events_df()
    assert player_event_counts(df, player_id=1) == {"rating": 3, "goal": 1}


def test_team_form_last_three():
    df = pl.DataFrame({
        "match_date":    [date(2024, 1, 1), date(2024, 1, 8), date(2024, 1, 15), date(2024, 1, 22)],
        "goals_for":     [0, 2, 1, 3],
        "goals_against": [1, 2, 0, 0],
        "result":        ["L", "D", "W", "W"],
        "points":        [0, 1, 3, 3],
    })
    stats = team_form(df, window=3)
    assert stats == {
        "avg_goals_for": 2.0,
        "avg_goals_against": pytest.approx(2 / 3),
        "points": 7,
        "form": "DWW",
    }