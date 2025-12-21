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
    SELECT full_name,
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