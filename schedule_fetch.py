from dotenv import load_dotenv
import psycopg
import os
from datetime import date

from nba_fetch import (fetch_team_id, fetch_team_info, fetch_team_roster, fetch_team_schedule, fetch_player_game_logs)
from odds_fetch import fetch_odds

today = date.today()
load_dotenv()
dsn = os.getenv("DATABASE_URL")
lal_team_id = fetch_team_id("Los Angeles Lakers")

def run_all():
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            fetch_team_info(lal_team_id, cur)
            roster_df = fetch_team_roster(lal_team_id, cur)
            schedule_df = fetch_team_schedule(lal_team_id, "2025-26", cur)
            for _, row in roster_df.iterrows():
                fetch_player_game_logs(row['PLAYER_ID'], '2025-26', cur)
    
    fetch_odds(roster_df)

    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            print("Refreshing materialized views...")
            cur.execute("REFRESH MATERIALIZED VIEW rolling_stats;")
            cur.execute("REFRESH MATERIALIZED VIEW game_odds_pivot;")
            cur.execute("REFRESH MATERIALIZED VIEW player_odds_pivot;")
            cur.execute("REFRESH MATERIALIZED VIEW player_prop_results;")
            cur.execute("REFRESH MATERIALIZED VIEW game_props_results;")
            cur.execute("REFRESH MATERIALIZED VIEW model_player_stats;")

            print("Materialized views updated.")

        print("date: ", today)
if __name__ == "__main__":
    run_all()