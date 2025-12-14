from dotenv import load_dotenv
import psycopg
import os
from datetime import date
import time
import random

from nba_fetch import (fetch_all_teams, fetch_team_info, fetch_team_roster, fetch_team_schedule, fetch_player_game_logs, fetch_team_def_stats)
from odds_fetch import fetch_odds

today = date.today()
load_dotenv()
dsn = os.getenv("DATABASE_URL")
all_teams = fetch_all_teams()

lal_team_abbrev = "LAL"
lal_team_id = all_teams.loc[all_teams['abbreviation'] == lal_team_abbrev, 'id'].iloc[0]

def run_all():
    with psycopg.connect(dsn) as conn:
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
        
    fetch_odds(roster_df)

    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            print("Refreshing materialized views...")
            cur.execute("REFRESH MATERIALIZED VIEW rolling_stats;")
            cur.execute("REFRESH MATERIALIZED VIEW game_odds_pivot;")
            cur.execute("REFRESH MATERIALIZED VIEW player_odds_pivot;")
            cur.execute("REFRESH MATERIALIZED VIEW team_def_stats;")
            cur.execute("REFRESH MATERIALIZED VIEW model_player_stats;")

            print("Materialized views updated.")

        print("date: ", today)
if __name__ == "__main__":
    run_all()