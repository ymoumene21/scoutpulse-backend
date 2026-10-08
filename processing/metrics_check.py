import asyncio
from processing.metrics import (
    fetch_events_df,
    fetch_team_matches_df,
    rolling_avg_rating,
    player_event_counts,
    team_form,
)


async def main():
    df = await fetch_events_df()
    print(df)

    print("Haaland rolling avg rating:", rolling_avg_rating(df, 1, 5))
    print("Haaland event counts:", player_event_counts(df, 1))

    arsenal = await fetch_team_matches_df("Arsenal")
    print(arsenal)
    print("Arsenal form (last 5):", team_form(arsenal, 5))
    print("Arsenal form (last 10):", team_form(arsenal, 10))


if __name__ == "__main__":
    asyncio.run(main())