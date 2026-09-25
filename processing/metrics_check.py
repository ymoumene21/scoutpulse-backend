import asyncio
from processing.metrics import fetch_events_df, rolling_avg_rating, player_event_counts, fetch_team_matches_df


async def main():
    df = await fetch_events_df()
    print(df)
    print(df.schema)  # column types Polars inferred — check this closely

    avg = await rolling_avg_rating(player_id=1, window=5)  # Haaland
    print("Haaland rolling avg rating:", avg)

    counts = await player_event_counts(player_id=1)  # Haaland
    print("Haaland event counts:", counts)

    team_df = await fetch_team_matches_df("Arsenal")
    print(team_df)


if __name__ == "__main__":
    asyncio.run(main())

