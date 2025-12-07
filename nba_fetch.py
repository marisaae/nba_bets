from nba_api.stats.static import teams
from nba_api.stats.endpoints import teaminfocommon, commonteamroster, scheduleleaguev2, playergamelog, teamgamelog
from tabulate import tabulate
import pandas as pd
import time
import random
import json

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
    cur.execute("""
        INSERT INTO team_info
        (id, team_name, abbreviation, location, conference, record, total_win, total_loss, standing)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (id) DO UPDATE SET
            record = EXCLUDED.record,
            total_win = EXCLUDED.total_win,
            total_loss = EXCLUDED.total_loss,
            standing = EXCLUDED.standing,
            last_updated = NOW();
    """, (team_id, team_name, team_abbreviation, team_city, team_conference, team_record, team_wins, team_losses, team_conf_rank))

 # Fetch team roster
def fetch_team_roster(team_id, cur):
    roster = commonteamroster.CommonTeamRoster(team_id=team_id)
    roster_df = roster.get_data_frames()[0]
    # print(tabulate(roster_df, headers='keys', tablefmt='psql'))

    if not roster_df.empty:
        for _, row in roster_df.iterrows():
            team_id = row['TeamID']
            player_id = row['PLAYER_ID']
            full_name = row['PLAYER']
            first_name = row['PLAYER'].split(' ')[0]
            last_name = row['PLAYER'].split(' ')[1]
            age = row['AGE']
            number = row['NUM']
            position = row['POSITION']
            raw_height = row['HEIGHT']
            feet, inches = raw_height.split("-")
            formatted_height = f"{feet}'{inches}\""
            weight = row['WEIGHT'] + " lbs"

            cur.execute("""
                INSERT INTO roster (player_id, team_id, full_name, first_name, last_name, age, number, position, height, weight)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (player_id) DO UPDATE SET
                    age = EXCLUDED.age,
                    number = EXCLUDED.number,
                    position = EXCLUDED.position,
                    height = EXCLUDED.height,
                    weight = EXCLUDED.weight,
                    last_updated = NOW();
            """, (player_id, team_id, full_name, first_name, last_name, age, number, position, formatted_height, weight))
    else:
        print("No team roster data found.")
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
        'awayTeam_teamId',
        'awayTeam_teamName',
        'arenaName',
        'arenaCity',
        'arenaState'
    ]
    schedule_df["gameDate"] = pd.to_datetime(schedule_df["gameDate"])
    schedule_df = schedule_df[columns].sort_values(["schedule_teamId", "gameDate"]).reset_index(drop=True)
    schedule_df["is_b2b"] = (schedule_df.groupby("schedule_teamId")["gameDate"].diff().dt.days == 1)

    if not schedule_df.empty:
        for _, row in schedule_df.iterrows():
            game_id = row['gameId']
            game_label = row['gameLabel']
            season_year = row['seasonYear']
            game_date = row['gameDate']
            game_status = row['gameStatusText']
            home_team_id = row['homeTeam_teamId']
            home_team_name = row['homeTeam_teamName']
            away_team_id = row['awayTeam_teamId']
            away_team_name = row['awayTeam_teamName']
            arena_name = row['arenaName']
            arena_city = row['arenaCity']
            arena_state = row['arenaState']
            is_home = (row['homeTeam_teamId'] == team_id)
            is_b2b = row['is_b2b']

            cur.execute("""
                INSERT INTO schedule (game_id, game_label, season_year, game_date, game_status, home_team_id, home_team_name, away_team_id, away_team_name, arena_name, arena_city, arena_state, is_home, is_b2b)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (game_id) DO UPDATE SET
                    game_status = EXCLUDED.game_status,
                    is_b2b = EXCLUDED.is_b2b,
                    last_updated = NOW();
            """, (game_id, game_label, season_year, game_date, game_status, home_team_id, home_team_name, away_team_id, away_team_name, arena_name, arena_city, arena_state, is_home, is_b2b))
    else:
        print("No schedule data found.")

    return schedule_df

# Fetch team game logs
def fetch_team_game_logs(team_id, game_id, season, cur, max_retries=3, wait_seconds=5):
    game_log_df = pd.DataFrame()
    for attempt in range(max_retries):
        try:
            time.sleep(random.uniform(0.7, 1.4))
            team_game_log = teamgamelog.TeamGameLog(team_id=team_id, season=season)
            game_log_df = team_game_log.get_data_frames()[0]
            break   
        except Exception as e:
            print(f"Attempt {attempt+1} failed for team ID {team_id}: {e}")
            time.sleep(wait_seconds)

    if game_log_df.empty:
        print(f"No game log data found for team ID {team_id}.")

    filtered_game_log = game_log_df[game_log_df["Game_ID"] == game_id]

    if filtered_game_log.empty:
        print(f"Team {team_id} did not play game {game_id} (yet).")
        return

    for _, log_row in filtered_game_log.iterrows():
        game_id = log_row['Game_ID']
        game_date = log_row['GAME_DATE']
        matchup = log_row['MATCHUP']
        win_loss = log_row['WL']
        points = log_row['PTS']

        cur.execute("""
            INSERT INTO team_game_log (team_id, game_id, game_date, matchup, wl, pts)
            VALUES (%s,%s,%s,%s,%s,%s)
            ON CONFLICT (team_id, game_id) DO UPDATE SET
                wl = EXCLUDED.wl,
                pts = EXCLUDED.pts,
                last_updated = NOW();
        """, (team_id, game_id, game_date, matchup, win_loss, points))


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

    for _, log_row in player_log_df.iterrows():
        game_id = log_row['Game_ID']
        game_date = log_row['GAME_DATE']
        matchup = log_row['MATCHUP']
        player_id = log_row['Player_ID']
        win_loss = log_row['WL']
        minutes = log_row['MIN']
        points = log_row['PTS']
        fieldgoals_made = log_row['FGM']
        fieldgoals_attempted = log_row['FGA']
        fieldgoals_percent = log_row['FG_PCT']
        threepoints_made = log_row['FG3M']
        threepoints_attempted = log_row['FG3A']
        threepoints_percent = log_row['FG3_PCT']
        freethrows_made = log_row['FTM']
        freethrows_attempted = log_row['FTA']
        freethrows_percent = log_row['FT_PCT']
        off_rebounds = log_row['OREB']
        def_rebounds = log_row['DREB']
        rebounds = log_row['REB']
        assists = log_row['AST']
        steals = log_row['STL']
        blocks = log_row['BLK']
        turnovers = log_row['TOV']
        fouls = log_row['PF']
        pts_reb_ast = log_row['PTS'] + log_row['REB'] + log_row['AST']

        cur.execute("""
            INSERT INTO player_game_log (player_id, game_id, game_date, matchup, wl, min, pts, fgm, fga, fg_pct, three_pts_made, three_pts_att, three_pts_pct, ftm, fta, ft_pct, oreb, dreb, tot_reb, ast, stl, blk, turnover, fouls, pts_reb_ast)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
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
                """, (player_id, game_id, game_date, matchup, win_loss, minutes, points, fieldgoals_made, fieldgoals_attempted, fieldgoals_percent, threepoints_made, threepoints_attempted, threepoints_percent, freethrows_made, freethrows_attempted, freethrows_percent, off_rebounds, def_rebounds, rebounds, assists, steals, blocks, turnovers, fouls, pts_reb_ast))