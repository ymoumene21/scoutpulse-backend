from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel

from api.db import player_exists, team_exists
from processing.metrics import (
    fetch_events_df, fetch_team_matches_df,
    rolling_avg_rating, player_event_counts, team_form,
)
app = FastAPI()


# ---------- Response models ----------

class PerformanceResponse(BaseModel):
    player_id: int
    window: int
    average_rating: float | None


class PlayerStats(BaseModel):
    player_id: int
    average_rating: float | None
    event_counts: dict[str, int]


class CompareResponse(BaseModel):
    window: int
    players: list[PlayerStats]

class TeamTrendsResponse(BaseModel):
    team: str
    window: int
    avg_goals_for: float | None
    avg_goals_against: float | None
    points: int
    form: str


# ---------- Endpoints ----------

@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/players/compare", response_model=CompareResponse)
async def compare_players(
    ids: list[int] = Query(),
    window: int = 5,
    min_matches: int = 1,
):
    for pid in ids:
        if not await player_exists(pid):
            raise HTTPException(status_code=404, detail=f"Player {pid} not found")

    df = await fetch_events_df()          # ONE fetch for the whole request

    players = []
    for pid in ids:
        avg = rolling_avg_rating(df, pid, window)
        counts = player_event_counts(df, pid)
        if sum(counts.values()) < min_matches:
            continue
        players.append(PlayerStats(player_id=pid, average_rating=avg, event_counts=counts))
    return CompareResponse(window=window, players=players)


@app.get("/players/{id}/performance", response_model=PerformanceResponse)
async def get_performance(id: int, window: int = 5):
    if not await player_exists(id):
        raise HTTPException(status_code=404, detail=f"Player {id} not found")

    df = await fetch_events_df()
    avg = rolling_avg_rating(df, id, window)
    return PerformanceResponse(player_id=id, window=window, average_rating=avg)


@app.get("/teams/{team}/trends", response_model=TeamTrendsResponse)
async def get_team_trends(team: str, window: int = 5):
    if not await team_exists(team):
        raise HTTPException(status_code=404, detail=f"Team {team} not found")

    df = await fetch_team_matches_df(team)
    stats = team_form(df, window)
    return TeamTrendsResponse(team=team, window=window, **stats)