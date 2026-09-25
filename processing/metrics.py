"""
Processing layer: pulls match_events rows out of Postgres and into a
Polars DataFrame, and computes performance metrics (rolling averages,
event counts) for the API layer to serve.
"""

import polars as pl
from api.db import get_pool  # same connection pool from Day 2/3


async def fetch_events_df() -> pl.DataFrame:
    """
    Pull every match_event, joined with the player's name/team and the
    match's date, into one flat Polars DataFrame.

    The join happens in SQL (Postgres already does joins well) — Polars'
    job starts after that, with the flat result. event_value is cast to
    float8 in SQL so it arrives as a plain float, not a Decimal Polars
    can't safely infer a type for.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT
                me.id,
                me.match_id,
                me.player_id,
                p.name AS player_name,
                p.team,
                m.match_date,
                me.event_type,
                me.event_value::float8 AS event_value,
                me.minute
            FROM match_events me
            JOIN players p ON p.id = me.player_id
            JOIN matches m ON m.id = me.match_id
            ORDER BY m.match_date
            """
        )

    # asyncpg returns Record objects (dict-like). Polars builds a
    # DataFrame straight from a list of plain dicts.
    return pl.DataFrame([dict(row) for row in rows])


async def rolling_avg_rating(player_id: int, window: int = 5) -> float | None:
    """
    Average of a player's most recent `window` rating events.
    Mirrors the /players/{id}/performance?window= endpoint from Day 5.
    """
    df = await fetch_events_df()

    ratings = (
        df
        .filter(
            (pl.col("player_id") == player_id) &
            (pl.col("event_type") == "rating")
        )
        .sort("match_date")
        .tail(window)
    )

    if ratings.is_empty():
        return None

    return ratings["event_value"].mean()


async def player_event_counts(player_id: int) -> dict[str, int]:
    """
    Counts every event type a player has recorded (goals, assists, cards, etc.).
    """
    df = await fetch_events_df()

    counts = (
        df
        .filter(pl.col("player_id") == player_id)
        .group_by("event_type")
        .agg(pl.len().alias("count"))
    )

    return dict(zip(counts["event_type"], counts["count"]))


async def fetch_team_matches_df(team: str) -> pl.DataFrame:
    """
    One team's season from its own perspective: goals for/against,
    W/D/L and points per match. SQL reshapes each row (CASE + CTEs);
    Polars does the cross-row maths afterwards.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            WITH team_matches AS (
                SELECT match_date,
                       CASE WHEN home_team = $1 THEN home_score ELSE away_score END AS goals_for,
                       CASE WHEN away_team = $1 THEN home_score ELSE away_score END AS goals_against
                FROM matches
                WHERE home_team = $1 OR away_team = $1
            ), match_status AS (
                SELECT *,
                       CASE
                           WHEN goals_for > goals_against THEN 'W'
                           WHEN goals_for = goals_against THEN 'D'
                           ELSE 'L'
                       END AS result
                FROM team_matches
            )
            SELECT *,
                   CASE WHEN result = 'W' THEN 3
                        WHEN result = 'D' THEN 1
                        ELSE 0
                   END AS points
            FROM match_status
            ORDER BY match_date
            """,
            team,
        )

    return pl.DataFrame([dict(row) for row in rows])