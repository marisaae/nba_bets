from db.queries import get_team_info, get_team_schedule, get_team_roster, get_player_stats, get_all_player_props, get_player_props
import pandas as pd

def load_team_schedule(team_id):
    df = get_team_schedule(team_id)
    return df


def load_team_roster(team_id):
    df = get_team_roster(team_id)
    return df


def load_player_stats(player_id, curr_season):
    df = get_player_stats(player_id, curr_season)
    df['game_date'] = pd.to_datetime(df['game_date']).dt.strftime("%m/%d/%Y")
    return df

def load_team_info(team_id):
    df = get_team_info(team_id)
    return df

def load_player_props(player_id):
    df = get_player_props(player_id)
    df['game_date'] = pd.to_datetime(df['game_date']).dt.strftime("%m/%d/%Y")
    return df

def load_all_player_props():
    df = get_all_player_props()
    df['game_date'] = pd.to_datetime(df['game_date']).dt.strftime("%m/%d/%Y")
    return df