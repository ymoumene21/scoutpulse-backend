"""
Reads raw match event data from a CSV, validates every row through
RawMatchEvent, and inserts only the clean rows into Postgres.
Rows that fail -- at validation OR at the database -- are reported,
never silently dropped.
"""

import asyncio
import csv
from pathlib import Path

import asyncpg
from pydantic import ValidationError

from api.db import get_pool
from ingestion.schemas import RawMatchEvent

CSV_PATH = Path(__file__).parent / "raw_events.csv"


def clean_row(row: dict) -> dict:
    """CSV cells are always strings; a truly empty cell arrives as "" not None.
    Convert "" to real None so Pydantic treats it as 'missing', not 'invalid'."""
    return {key: (value if value != "" else None) for key, value in row.items()}


async def ingest():
    pool = await get_pool()
    inserted = 0
    rejected = 0

    with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for line_number, raw_row in enumerate(reader, start=2):  # row 1 is the header
            cleaned = clean_row(raw_row)

            # Checkpoint 1: is this row shaped correctly?
            try:
                event = RawMatchEvent.model_validate(cleaned)
            except ValidationError as e:
                print(f"[REJECTED - validation] line {line_number}: {e}")
                rejected += 1
                continue

            # Checkpoint 2: does the database actually accept it?
            try:
                async with pool.acquire() as conn:
                    await conn.execute(
                        """
                        INSERT INTO match_events (match_id, player_id, event_type, event_value, minute)
                        VALUES ($1, $2, $3, $4, $5)
                        """,
                        event.match_id, event.player_id, event.event_type,
                        event.event_value, event.minute,
                    )
                inserted += 1
            except asyncpg.PostgresError as e:
                print(f"[REJECTED - database] line {line_number}: {e}")
                rejected += 1

    print(f"\nDone. Inserted: {inserted}. Rejected: {rejected}.")


if __name__ == "__main__":
    asyncio.run(ingest())
