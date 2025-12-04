from dateutil import parser
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from utils import normalize_name, get_json
import psycopg
import os

load_dotenv()
api_key = os.getenv("ODDSAPI_KEY")
sport = "basketball_nba"
region = "us"
game_markets = "h2h,totals"
player_markets = "player_points,player_rebounds,player_assists,player_points_rebounds_assists,player_threes,player_blocks,player_steals,player_turnovers,player_field_goals"
odds_format = "american"
date_format = "iso"
bookmakers = "draftkings"
dsn = os.getenv("DATABASE_URL")

def fetch_odds(roster_df):
    get_events_path = f"/v4/sports/{sport}/events?apiKey={api_key}&dateFormat={date_format}"

    # fetch event data 
    events = get_json(get_events_path)
    est = ZoneInfo("America/New_York")
    lakers_events = []
    for event in events:
        home = event['home_team']
        away = event['away_team']
        if "Lakers" in home or "Lakers" in away:
            lakers_events.append(event)

    for event in lakers_events:
        try:
            if event.get('commence_time') is None:
                print(f"Skipping event {event['id']} — missing commence_time")
                continue

            try:
                game_date = parser.parse(event['commence_time']).date()
            except Exception as e:
                print(f"Error parsing date for event {event['id']}: {e}")
                continue

            event_id = event['id']
            game_date = parser.parse(event['commence_time']).astimezone(est).date()
            home_team = event['home_team'].split(" ")[-1]
            away_team = event['away_team'].split(" ")[-1]

            # fetch overall odds data for game
            event_odds_path = f"/v4/sports/{sport}/events/{event_id}/odds?apiKey={api_key}&regions={region}&markets={game_markets}&oddsFormat={odds_format}&bookmakers={bookmakers}"
            event_odds = get_json(event_odds_path)
            
            if event_odds is None:
                print(f"No odds data for event {event_id}")
                continue
            
            event_bookmakers_list = event_odds.get('bookmakers', [])
            if len(event_bookmakers_list) == 0:
                print(f"DraftKings odds not available for event {event_id}")
                continue
            
            event_bm = event_bookmakers_list[0]
            bookmaker = event_bm.get('key')

            game_odds_rows_to_insert = []
            for market in event_bm.get('markets', []):
                market_key = market.get('key')
                last_odds_update = market.get('last_update')
                for outcome in market.get('outcomes', []):
                    outcome_name = outcome.get('name')
                    price = outcome.get('price')
                    point = outcome.get('point')
                    game_odds_rows_to_insert.append((event_id, bookmaker, market_key, outcome_name, price, point, last_odds_update))

            if not game_odds_rows_to_insert:
                print(f"No outcomes to insert for event {event_id}")
                continue        

            # fetch player odds data for game
            player_odds_path = f"/v4/sports/{sport}/events/{event_id}/odds?apiKey={api_key}&regions={region}&markets={player_markets}&oddsFormat={odds_format}&bookmakers={bookmakers}"
            event_player_odds = get_json(player_odds_path)
            roster_names = set(roster_df['PLAYER'])
            roster_names_norm = {normalize_name(n) for n in roster_names}

            if event_player_odds is None:
                print(f"No player odds data for event {event_id}")
                continue
            
            player_bookmakers_list = event_player_odds.get('bookmakers', [])
            if len(player_bookmakers_list) == 0:
                print(f"DraftKings odds not available for event {event_id}")
                continue
            
            player_bm = player_bookmakers_list[0]
            player_bookmaker = player_bm.get('key')

            player_odds_rows_to_insert = []
            for market in player_bm.get('markets', []):
                market_key = market.get('key')
                last_odds_update = market.get('last_update')
                for outcome in market.get('outcomes', []):
                    player_name = outcome.get('description')
                    player_name_norm = normalize_name(player_name)
                    if player_name_norm not in roster_names_norm:
                        continue

                    outcome_name = outcome.get('name')
                    price = outcome.get('price')
                    point = outcome.get('point')

                    player_odds_rows_to_insert.append((event_id, player_bookmaker, market_key, outcome_name, player_name, price, point, last_odds_update))

            if not player_odds_rows_to_insert:
                print(f"No player outcomes to insert for event {event_id}")
                continue   

            with psycopg.connect(dsn) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE schedule
                        SET event_id = %s
                        WHERE game_date = %s AND home_team_name = %s AND away_team_name = %s;
                    """, (event_id, game_date, home_team, away_team))

                    if cur.rowcount == 0:
                        print(f"No matching schedule row for event {event_id} ({home_team} vs {away_team} on {game_date})")
                    else:
                        print(f"Event {event_id} inserted into schedule.")

                    for row in game_odds_rows_to_insert:
                        cur.execute("""
                            INSERT INTO game_odds (event_id, bookmaker, market, outcome_name, price, point, last_odds_update)
                            VALUES (%s,%s,%s,%s,%s,%s,%s)
                            ON CONFLICT (event_id, bookmaker, market, outcome_name) DO UPDATE SET
                                price = EXCLUDED.price,
                                point = EXCLUDED.point,
                                last_odds_update = EXCLUDED.last_odds_update,
                                last_updated = NOW();
                        """, row)

                        print (f"Updated {len(game_odds_rows_to_insert)} odds rows for event {event_id}.")

                    for row in player_odds_rows_to_insert:
                        cur.execute("""
                            INSERT INTO player_odds (event_id, bookmaker, market, outcome_name, player_name, price, point, last_odds_update)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                            ON CONFLICT (event_id, bookmaker, market, outcome_name, player_name) DO UPDATE SET
                                price = EXCLUDED.price,
                                point = EXCLUDED.point,
                                last_odds_update = EXCLUDED.last_odds_update,
                                last_updated = NOW();
                        """, row)
                        print (f"Updated {len(player_odds_rows_to_insert)} player odds rows for event {event_id}.")
                        
        except Exception as e:
            print(f"Unexpected error processing event {event.get('id', 'UNKNOWN')}: {e}")
            continue