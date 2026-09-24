# api/db.py
import asyncpg

# Matches the credentials we set in docker-compose.yml.
DATABASE_URL = "postgresql://scoutpulse:scoutpulse_dev@localhost:5432/scoutpulse"

_pool: asyncpg.Pool | None = None  # created once, reused for the app's lifetime


async def get_pool() -> asyncpg.Pool:
    """Create the pool on first use, then just return the same one every time."""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    return _pool


async def get_player_events(player_id: int):
    """Our one working async query: every event for a player, joined with its match."""
    pool = await get_pool()
    async with pool.acquire() as conn:          # borrow a connection from the pool
        rows = await conn.fetch(                # await = don't block while Postgres runs this
            """
            SELECT p.name, e.event_type, e.minute, e.event_value,
                   m.home_team, m.away_team, m.match_date
            FROM match_events e
            JOIN players p ON p.id = e.player_id
            JOIN matches m ON m.id = e.match_id
            WHERE e.player_id = $1
            ORDER BY m.match_date, e.minute;
            """,
            player_id,                          # $1 is a placeholder -- prevents SQL injection
        )
    return [dict(row) for row in rows]


async def player_exists(player_id: int) -> bool:
    pool = await get_pool()
    row = await pool.fetchrow("SELECT 1 FROM players WHERE id = $1", player_id)
    return row is not None