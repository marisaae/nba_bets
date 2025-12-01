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
                if player_name not in roster_names:
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
                        INSERT INTO game_odds (event_id, bookmaker, market, outcome_name, player_name, price, point, last_odds_update)
                        VALUES (%s,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT (event_id, bookmaker, market, outcome_name, player_name) DO UPDATE SET
                            price = EXCLUDED.price,
                            point = EXCLUDED.point,
                            last_odds_update = EXCLUDED.last_odds_update,
                            last_updated = NOW();
                    """, row)
                    print (f"Updated {len(player_odds_rows_to_insert)} player odds rows for event {event_id}.")