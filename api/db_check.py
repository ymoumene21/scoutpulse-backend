# api/db_check.py — manual check that our async DB layer works end-to-end
import asyncio
from api.db import get_player_events

async def main():
    events = await get_player_events(1)  # Erling Haaland's player id
    for e in events:
        print(e)

if __name__ == "__main__":
    asyncio.run(main())