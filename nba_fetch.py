from nba_api.stats.static import teams
from nba_api.stats.endpoints import teaminfocommon, commonteamroster, scheduleleaguev2, playergamelog
from tabulate import tabulate
import pandas as pd
import time
import random

# Fetch team ID by team name
def fetch_team_id(team_name):
    nba_teams = teams.get_teams()
    for team in nba_teams:
        if team['full_name'] == team_name:
            return team['id']


# Fetch team info
def fetch_team_info(team_id, cur):
    team_info = teaminfocommon.TeamInfoCommon(team_id=team_id)
    team_df = team_info.get_data_frames()[0]

    if team_df.empty:
        print("No team data found.")
        return

    # extract values
    team_name = team_df.loc[0, 'TEAM_NAME']
    team_abbreviation = team_df.loc[0, 'TEAM_ABBREVIATION']
    team_city = team_df.loc[0, 'TEAM_CITY']
    team_conference = team_df.loc[0, 'TEAM_CONFERENCE']
    team_record = f"{team_df.loc[0, 'W']}-{team_df.loc[0, 'L']}"
    team_wins = team_df.loc[0, 'W']
    team_losses = team_df.loc[0, 'L']
    team_conf_rank = team_df.loc[0, 'CONF_RANK']

    # insert or update team info in the database
    query = """
        INSERT INTO team_info
        (id, team_name, abbreviation, location, conference, record, total_win, total_loss, standing)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (id) DO UPDATE SET
            record = EXCLUDED.record,
            total_win = EXCLUDED.total_win,
            total_loss = EXCLUDED.total_loss,
            standing = EXCLUDED.standing,
            last_updated = NOW();
    """
    cur.execute(query, (team_id, team_name, team_abbreviation, team_city, team_conference, team_record, team_wins, team_losses, team_conf_rank))

 # Fetch team roster
def fetch_team_roster(team_id, cur):
    roster = commonteamroster.CommonTeamRoster(team_id=team_id)
    roster_df = roster.get_data_frames()[0]
    # print(tabulate(roster_df, headers='keys', tablefmt='psql'))
    rows_to_insert = []
    if not roster_df.empty:
        for _, row in roster_df.iterrows():
            player_id = row['PLAYER_ID']
            full_name = row['PLAYER']
            first_name = row['PLAYER'].split(' ')[0]
            last_name = row['PLAYER'].split(' ')[1]
            age = row['AGE']
            number = row['NUM']
            position = row['POSITION']
            raw_height = row['HEIGHT']
            feet, inches = raw_height.split("-")
            height = f"{feet}'{inches}\""
            weight = row['WEIGHT'] + " lbs"
            rows_to_insert.append((team_id, player_id, full_name, first_name, last_name, age, number, position, height, weight))
    else:
        print("No team roster data found.")

    query = """
                INSERT INTO roster (team_id, player_id, full_name, first_name, last_name, age, number, position, height, weight)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (player_id) DO UPDATE SET
                    age = EXCLUDED.age,
                    number = EXCLUDED.number,
                    position = EXCLUDED.position,
                    height = EXCLUDED.height,
                    weight = EXCLUDED.weight,
                    last_updated = NOW();
            """
    cur.executemany(query, rows_to_insert)

    return roster_df

# Fetch team schedule
def fetch_team_schedule(team_id, season, cur):
    league_schedule = scheduleleaguev2.ScheduleLeagueV2(season=season)
    schedule_df = league_schedule.get_data_frames()[0]
    schedule_df = schedule_df[(schedule_df['homeTeam_teamId'] == team_id) | (schedule_df['awayTeam_teamId'] == team_id)]
    schedule_df['schedule_teamId'] = team_id
    columns = [
        'schedule_teamId',
        'gameId',
        'gameLabel',
        'seasonYear',
        'gameDate',
        'gameStatusText',
        'homeTeam_teamId',
        'homeTeam_teamName',
        'homeTeam_score',
        'awayTeam_teamId',
        'awayTeam_teamName',
        'awayTeam_score',
        'arenaName',
        'arenaCity',
        'arenaState',
    ]
    schedule_df["gameDate"] = pd.to_datetime(schedule_df["gameDate"])
    schedule_df = schedule_df[columns].sort_values(["schedule_teamId", "gameDate"]).reset_index(drop=True)
    schedule_df["is_b2b"] = (schedule_df.groupby("schedule_teamId")["gameDate"].diff().dt.days == 1)

    rows_to_insert = []
    if not schedule_df.empty:
        for _, row in schedule_df.iterrows():
            game_id = row['gameId']
            game_label = row['gameLabel']
            season_year = row['seasonYear']
            game_date = row['gameDate']
            game_status = row['gameStatusText']
            home_team_id = row['homeTeam_teamId']
            home_team_name = row['homeTeam_teamName']
            home_team_score = row['homeTeam_score']
            away_team_id = row['awayTeam_teamId']
            away_team_name = row['awayTeam_teamName']
            away_team_score = row['awayTeam_score']
            arena = row['arenaName']
            arena_city = row['arenaCity']
            arena_state = row['arenaState']
            is_home = (row['homeTeam_teamId'] == team_id)
            is_b2b = row['is_b2b']

            rows_to_insert.append((game_id, game_label, season_year, game_date, game_status, home_team_id, home_team_name, home_team_score, away_team_id, away_team_name, away_team_score, arena, arena_city, arena_state, is_home, is_b2b))
    else:
        print("No schedule data found.")
    query = """
        INSERT INTO schedule (game_id, game_label, season_year, game_date, game_status, home_team_id, home_team_name, home_team_score, away_team_id, away_team_name, away_team_score, arena_name, arena_city, arena_state, is_home, is_b2b)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (game_id) DO UPDATE SET
            game_status = EXCLUDED.game_status,
            is_b2b = EXCLUDED.is_b2b,
            home_team_score = EXCLUDED.home_team_score,
            away_team_score = EXCLUDED.away_team_score,
            last_updated = NOW();
        """
    cur.executemany(query, rows_to_insert)

    return schedule_df


# Fetch player game logs
def fetch_player_game_logs(player_id, season, cur, max_retries=3, wait_seconds=5):
    player_log_df = pd.DataFrame()
    for attempt in range(max_retries):
        try:
            time.sleep(random.uniform(0.7, 1.4))
            player_log = playergamelog.PlayerGameLog(player_id=player_id, season=season)
            player_log_df = player_log.get_data_frames()[0].drop(columns=['PLUS_MINUS', 'VIDEO_AVAILABLE'])
            player_log_df['GAME_DATE'] = pd.to_datetime(player_log_df['GAME_DATE']).dt.strftime('%Y-%m-%d')
            break   
        except Exception as e:
            print(f"Attempt {attempt+1} failed for player ID {player_id}: {e}")
            time.sleep(wait_seconds)

    if player_log_df.empty:
        print(f"No game log data found for player ID {player_id}.")

    rows_to_insert = []
    for _, log_row in player_log_df.iterrows():
            game_id = log_row['Game_ID']
            game_date = log_row['GAME_DATE']
            matchup = log_row['MATCHUP']
            wl = log_row['WL']
            min = log_row['MIN']
            pts = log_row['PTS']
            fgm = log_row['FGM']
            fga = log_row['FGA']
            fg_pct = log_row['FG_PCT']
            fg3m = log_row['FG3M']
            fg3a = log_row['FG3A']
            fg3_pct = log_row['FG3_PCT']
            ftm = log_row['FTM']
            fta = log_row['FTA']
            ft_pct = log_row['FT_PCT']
            oreb = log_row['OREB']
            dreb = log_row['DREB']
            tot_reb = log_row['REB']
            ast = log_row['AST']
            stl = log_row['STL']
            blk = log_row['BLK']
            tov = log_row['TOV']
            pf = log_row['PF']
            pra = log_row['PTS'] + log_row['REB'] + log_row['AST']
            
            rows_to_insert.append((player_id, game_id, game_date, matchup, wl, min, pts, fgm, fga, fg_pct, fg3m, fg3a, fg3_pct, ftm, fta, ft_pct, oreb, dreb, tot_reb, ast, stl, blk, tov, pf, pra))
    
    query = """
        INSERT INTO player_game_log (player_id, game_id, game_date, matchup, wl, min, pts, fgm, fga, fg_pct, three_pts_made, three_pts_att, three_pts_pct, ftm, fta, ft_pct, oreb, dreb, tot_reb, ast, stl, blk, turnover, fouls, pts_reb_ast)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (game_id, player_id) DO UPDATE SET
            wl = EXCLUDED.wl,
            min = EXCLUDED.min,
            pts = EXCLUDED.pts,
            fgm = EXCLUDED.fgm,
            fga = EXCLUDED.fga,
            fg_pct = EXCLUDED.fg_pct,
            three_pts_made = EXCLUDED.three_pts_made,
            three_pts_att = EXCLUDED.three_pts_att,
            three_pts_pct = EXCLUDED.three_pts_pct,
            ftm = EXCLUDED.ftm,
            fta = EXCLUDED.fta,
            ft_pct = EXCLUDED.ft_pct,
            oreb = EXCLUDED.oreb,
            dreb = EXCLUDED.dreb,
            tot_reb = EXCLUDED.tot_reb,
            ast = EXCLUDED.ast,
            stl = EXCLUDED.stl,
            blk = EXCLUDED.blk,
            turnover = EXCLUDED.turnover,
            fouls = EXCLUDED.fouls,
            pts_reb_ast = EXCLUDED.pts_reb_ast,
            last_updated = NOW();
        """       
    cur.executemany(query, rows_to_insert)