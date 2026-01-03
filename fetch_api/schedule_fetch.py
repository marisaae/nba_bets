from datetime import date
import os
import time
import random
from db.connection import get_connection

from fetch_api.nba_fetch import (fetch_all_teams, fetch_team_info, fetch_team_roster, fetch_team_schedule, fetch_player_game_logs, fetch_team_def_stats, fetch_player_headshot)
from fetch_api.odds_fetch import fetch_odds
from utils.fetch_utils import cleanup_old_headshots

today = date.today()
all_teams = fetch_all_teams()

lal_team_abbrev = "LAL"
lal_team_id = all_teams.loc[all_teams['abbreviation'] == lal_team_abbrev, 'id'].iloc[0]

def run_all():
    with get_connection() as conn:
        with conn.cursor() as cur:
            for _, row in all_teams.iterrows():
                team_id = row['id']
                fetch_team_info(team_id, cur)
                time.sleep(random.uniform(0.8, 1.5))
            roster_df = fetch_team_roster(lal_team_id, cur)
            fetch_team_schedule(lal_team_id, "2025-26", cur)
            fetch_team_def_stats('F', '2025-26', cur)
            fetch_team_def_stats('C', '2025-26', cur)
            fetch_team_def_stats('G', '2025-26', cur)
            for _, row in roster_df.iterrows():
                fetch_player_game_logs(row['PLAYER_ID'], '2025-26', cur)

    for _, row in roster_df.iterrows():
        player_id = row["PLAYER_ID"]  # or player_id
        filename = f"{player_id}.png"   # adjust naming if needed
        filepath = os.path.join("player_headshots", filename)

        # Skip if the file already exists
        if os.path.exists(filepath):
            print(f"{filename} already exists, skipping...")
            continue

        # Fetch and save photo
        fetch_player_headshot(player_id)
    
    current_player_ids = roster_df['PLAYER_ID'].tolist()
    cleanup_old_headshots(current_player_ids)

    fetch_odds(roster_df)

    with get_connection() as conn:
        with conn.cursor() as cur:
            print("Refreshing materialized views...")
            cur.execute("REFRESH MATERIALIZED VIEW rolling_stats;")
            cur.execute("REFRESH MATERIALIZED VIEW game_odds_pivot;")
            cur.execute("REFRESH MATERIALIZED VIEW player_odds_pivot;")
            cur.execute("REFRESH MATERIALIZED VIEW model_player_stats;")
            cur.execute("REFRESH MATERIALIZED VIEW front_end_props;")

            print("Materialized views updated.")

    print("date: ", today)
if __name__ == "__main__":
    run_all()