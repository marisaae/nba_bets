import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv("SQLALCHEMY_URL"))

def get_team_info(team_id):
    query = """
    SELECT  team_name,
            abbreviation,
            location,
            conference,
            record,
            total_win,
            total_loss,
            standing
        FROM team_info
        WHERE id = %s;
    """
    return pd.read_sql(query, engine, params=(team_id,))

def get_team_schedule(team_id):
    query = """
    SELECT  game_label,
            season_year, 
            game_date, 
            game_status, 
            home_team_id,
            home_team_name, 
            home_team_score, 
            away_team_id,
            away_team_name, 
            away_team_score, 
            arena_name
        FROM schedule
        WHERE home_team_id = %s OR away_team_id = %s
        ORDER BY game_date ASC;
    """
    return pd.read_sql(query, engine, params=(team_id, team_id))

def get_team_roster(team_id):
    query = """
    SELECT player_id,
           full_name,
           age,
           number,
           position,
           height,
           weight
        FROM roster
        WHERE team_id = %s
        ORDER BY full_name ASC;
    """
    return pd.read_sql(query, engine, params=(team_id,))

def get_player_stats(player_id, curr_season):
    query = """
    SELECT player_id,
           season,
           game_date,
           matchup,
           wl,
           min,
           pts,
           fgm,
           fga,
           fg_pct,
           three_pts_made,
           three_pts_att,
           three_pts_pct,
           ftm,
           fta,
           ft_pct,
           oreb,
           dreb,
           tot_reb,
           ast,
           stl,
           blk,
           turnover,
           fouls
        FROM player_game_log
        WHERE player_id = %s AND season = %s
        ORDER BY game_date DESC;
    """
    return pd.read_sql(query, engine, params=(player_id, curr_season))

def get_player_props(player_id, event_id, market):
    query="""
    SELECT *
    FROM front_end_props
    WHERE player_id = %s AND event_id = %s AND market = %s;
    """
    return pd.read_sql(query, engine, params=(player_id, event_id, market))

def get_all_player_props(event_id):
    query="""
    SELECT *
    FROM front_end_props
    WHERE event_id = %s;
    """
    return pd.read_sql(query, engine, params=(event_id,))

def get_next_game(team_id):
    query="""
    SELECT *
    FROM schedule
    WHERE (home_team_id = %s OR away_team_id = %s)
    AND game_date >= CURRENT_DATE
    AND game_status != 'Final'
    ORDER BY game_date ASC
    LIMIT 1;
    """
    
    df = pd.read_sql(query, engine, params=(team_id, team_id))

    if df.empty:
        return None

    return df.iloc[0].to_dict()