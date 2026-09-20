import asyncio
from processing.metrics import fetch_events_df, rolling_avg_rating, player_event_counts


async def main():
    df = await fetch_events_df()
    print(df)
    print(df.schema)  # column types Polars inferred — check this closely

    avg = await rolling_avg_rating(player_id=1, window=5)  # Haaland
    print("Haaland rolling avg rating:", avg)

    counts = await player_event_counts(player_id=1)  # Haaland
    print("Haaland event counts:", counts)


if __name__ == "__main__":
    asyncio.run(main())