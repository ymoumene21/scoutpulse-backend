from datetime import date

import polars as pl
import pytest
from fastapi.testclient import TestClient

import api.main
from api.main import app


# ---------- Fake data (same idea as test_metrics.py) ----------

def make_events_df():
    return pl.DataFrame({
        "player_id":   [1, 1, 1, 1, 2],
        "match_date":  [date(2024, 1, 1), date(2024, 1, 8), date(2024, 1, 15), date(2024, 1, 15), date(2024, 1, 1)],
        "event_type":  ["rating", "rating", "rating", "goal", "rating"],
        "event_value": [6.0, 7.0, 9.0, None, 5.0],
    })


def make_team_df():
    return pl.DataFrame({
        "match_date":    [date(2024, 1, 1), date(2024, 1, 8), date(2024, 1, 15)],
        "goals_for":     [0, 2, 1],
        "goals_against": [1, 2, 0],
        "result":        ["L", "D", "W"],
        "points":        [0, 1, 3],
    })


# ---------- Fake database functions ----------

async def fake_player_exists(player_id):
    return player_id in (1, 2)

async def fake_fetch_events_df():
    return make_events_df()

async def fake_team_exists(team):
    return team == "Arsenal"

async def fake_fetch_team_matches_df(team):
    return make_team_df()


@pytest.fixture
def client(monkeypatch):
    # Swap the real DB functions inside api.main for the fakes above
    monkeypatch.setattr(api.main, "player_exists", fake_player_exists)
    monkeypatch.setattr(api.main, "fetch_events_df", fake_fetch_events_df)
    monkeypatch.setattr(api.main, "team_exists", fake_team_exists)
    monkeypatch.setattr(api.main, "fetch_team_matches_df", fake_fetch_team_matches_df)
    return TestClient(app)


# ---------- /players/{id}/performance ----------

def test_performance_returns_200_and_correct_shape(client):
    response = client.get("/players/1/performance?window=2")
    assert response.status_code == 200
    assert response.json() == {"player_id": 1, "window": 2, "average_rating": 8.0}


def test_performance_unknown_player_returns_404(client):
    response = client.get("/players/999/performance")
    assert response.status_code == 404
    assert response.json() == {"detail": "Player 999 not found"}


def test_performance_non_numeric_id_returns_422(client):
    response = client.get("/players/abc/performance")
    assert response.status_code == 422


# ---------- /players/compare ----------

def test_compare_returns_both_players(client):
    response = client.get("/players/compare?ids=1&ids=2&window=5")
    assert response.status_code == 200
    body = response.json()
    assert [p["player_id"] for p in body["players"]] == [1, 2]
    assert body["players"][0]["event_counts"] == {"rating": 3, "goal": 1}


def test_compare_with_one_unknown_player_returns_404(client):
    response = client.get("/players/compare?ids=1&ids=999")
    assert response.status_code == 404


# ---------- /teams/{team}/trends ----------

def test_team_trends_returns_200(client):
    response = client.get("/teams/Arsenal/trends?window=2")
    assert response.status_code == 200
    assert response.json() == {
        "team": "Arsenal", "window": 2,
        "avg_goals_for": 1.5, "avg_goals_against": 1.0,
        "points": 4, "form": "DW",
    }


def test_team_trends_unknown_team_returns_404(client):
    response = client.get("/teams/Barcelona/trends")
    assert response.status_code == 404