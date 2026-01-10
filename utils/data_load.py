from db.queries import get_team_info, get_team_schedule, get_team_roster, get_player_stats, get_all_player_props, get_player_props, get_rolling_avg_stats, get_player_next_predictions
from utils.data_format import format_predictions
from utils.market_mappings import MARKET_TO_PRED_COL
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


def load_player_props(player_id, event_id, prop_market):
    df = get_player_props(player_id, event_id, prop_market)
    df['game_date'] = pd.to_datetime(df['game_date']).dt.strftime("%m/%d/%Y")
    return df


def load_all_player_props(event_id):
    df = get_all_player_props(event_id)
    df['game_date'] = pd.to_datetime(df['game_date']).dt.strftime("%m/%d/%Y")
    return df


def load_rolling_avg_stats(player_id):
    df = get_rolling_avg_stats(player_id)
    return df


def load_player_prediction(player_id, market):
    df = get_player_next_predictions(player_id)
    df = format_predictions(df)
    col_name = MARKET_TO_PRED_COL.get(market)

    if col_name is None or df.empty or col_name not in df.columns:
        return None

    value = df.iloc[0][col_name]

    return value
