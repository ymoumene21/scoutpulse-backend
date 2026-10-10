# scoutpulse-backend

An async FastAPI service that turns football match data into player and team performance metrics: rolling ratings, side-by-side player comparisons, and team form over the last N matches.

**Live API docs:** https://scoutpulse-api.onrender.com/docs
(Free hosting: the first request after a quiet period can take about a minute while the server and database wake up.)

## The problem

Comparing two players' recent form, or a team's last five results, usually means cross-referencing stat sheets by hand. This project makes each of those questions a single API call, backed by a validated database and tested calculation logic.

## Architecture

```
raw CSV
   │
   ▼
ingestion/   Pydantic validates each row; bad rows are rejected and reported, clean rows inserted
   │
   ▼
PostgreSQL   players · matches · match_events (foreign keys, CHECK and UNIQUE constraints)
   │
   ▼
processing/  SQL does the joins and labels rows; Polars does the maths (pure functions)
   │
   ▼
api/         FastAPI async endpoints, 404/422 handling, Pydantic response models → JSON
```

## Endpoints

| Endpoint | Returns |
|---|---|
| `GET /health` | `{"status": "ok"}` (no database call) |
| `GET /players/{id}/performance?window=5` | Player's average rating over their last `window` rated matches |
| `GET /players/compare?ids=1&ids=3&window=5&min_matches=1` | Rolling rating + event counts for several players side by side |
| `GET /teams/{team}/trends?window=5` | Team's average goals for/against, points and W/D/L form string over the last `window` matches (team given by name, e.g. `Arsenal`) |

Try it:
- https://scoutpulse-api.onrender.com/players/1/performance?window=5
- https://scoutpulse-api.onrender.com/teams/Arsenal/trends?window=5

Unknown players or teams return **404**; malformed parameters (e.g. `/players/abc/performance`) return **422**.

## Data

- **Matches:** all 380 real 2023/24 Premier League fixtures and scores from football-data.co.uk, cleaned and bulk-loaded into Postgres.
- **Players and match events:** football-data.co.uk only provides match-level data, so 5 real players and a small set of events (goals, ratings, cards) were hand-seeded on top of real fixtures. Player metrics are therefore a demonstration of the pipeline, not a full dataset.

## Engineering decisions

- **Async FastAPI + asyncpg pool:** endpoints spend most of their time waiting on the database, so async lets one process serve other requests while it waits; the pool reuses connections instead of opening one per request.
- **Validate at the door (Pydantic v2):** ingestion validates every CSV row before insert (types, allowed event types, minute 0–120). Database `UNIQUE`/`CHECK` constraints are a second layer that catches what a single row can't show (duplicates across rows).
- **SQL for joins and labelling, Polars for maths:** SQL CTEs turn each match into the team's perspective (goals for/against, W/D/L, points); Polars computes rolling averages and form.
- **Pure metric functions:** metric functions take a DataFrame instead of querying the database themselves, so each request fetches once, every calculation uses the same snapshot, and the functions are unit-testable without a database.
- **Cheap existence check first:** endpoints check the player/team exists (a one-row lookup) and return 404 before running the full fetch and calculations.
- **Configuration via environment variable:** `DATABASE_URL` is read from the environment with a local default, so the same code runs against local Docker Postgres and the hosted production database, and production credentials never enter the repo.

## Tests

```
pytest -v   →   16 passed
```

| File | Layer | What it checks |
|---|---|---|
| `tests/test_schemas.py` | Ingestion | Valid rows accepted, bad rows rejected (`pytest.raises`) |
| `tests/test_metrics.py` | Processing | Metric functions on small hand-built DataFrames with known answers |
| `tests/test_api.py` | API | Status codes (200/404/422) and response shapes, with database functions replaced by fakes |

No database is needed to run the tests.

## Deployment

- **API:** Render (free web service), built from this repo: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- **Database:** Neon (free serverless Postgres), connected through the `DATABASE_URL` environment variable

## Run locally

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
docker compose up -d                 # Postgres 16 on localhost:5433
uvicorn api.main:app --reload        # http://127.0.0.1:8000/docs
```

The schema is in `db/schema.sql` and seed data in `db/seed/`.

## Known limitations

- API tests mock the database, so the SQL itself is only verified manually against real results; integration tests against a test database would be the next step.
- The player-event layer is small and hand-seeded (see Data).
- `min_matches` in `/players/compare` currently counts events, not distinct matches.
- No caching; at this data size every request recomputes from a fresh query, which is fast enough.

## Stack

Python 3.14 · FastAPI · asyncpg · PostgreSQL · Polars · Pydantic v2 · pytest · Docker (local DB) · Render · Neon
