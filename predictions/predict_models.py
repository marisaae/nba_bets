import pandas as pd
from sqlalchemy import create_engine
import joblib
import os
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()
dsn = os.getenv("SQLALCHEMY_URL")
engine = create_engine(dsn)

query_model = "SELECT * FROM future_games;"
query_def = "SELECT * FROM team_def_stats;"

future_games_df = pd.read_sql(query_model, engine)
def_stats_df = pd.read_sql(query_def, engine)

future_games_df["primary_position"] = future_games_df["position"].str.split("-").str[0]
future_games_df = future_games_df.drop(columns=["position"])

prediction_df = future_games_df.merge(
    def_stats_df,
    left_on=["opp_team_id", "primary_position", "season"],
    right_on=["team_id", "opp_player_position", "season"],
    how="left"
)

prediction_df = prediction_df.drop(columns=["opp_team_id", "team_id", "team_name", "gp", "opp_player_position", "last_updated"])
prediction_df = prediction_df.rename(columns={"win_pct": "opp_wins_pct"})
prediction_df = prediction_df.fillna(0)

print(tabulate(prediction_df,headers='keys', tablefmt='fancy_grid'))

STAT_CONFIGS = {
    "points": {
        "target": "pts",
        "features": [
            "is_home", "is_b2b", "min_rolling_avg_over_5", "fga_rolling_avg_over_5", "fg_pct_rolling_avg_over_5", "pts_rolling_avg_over_5", "opp_pts", "opp_fg_pct", "opp_fg3_pct", "opp_oreb", "opp_fg_pct_rank", "opp_fg3_pct_rank"
        ]
    },

    "rebounds": {
        "target": "tot_reb",
        "features": [
            "is_home", "is_b2b", "min_rolling_avg_over_5", "reb_rolling_avg_over_5", "oreb_rolling_avg_over_5", "dreb_rolling_avg_over_5", "opp_oreb", "opp_dreb", "opp_reb"
        ]
    },

    "assists": {
        "target": "ast",
        "features": [
            "is_home", "is_b2b", "min_rolling_avg_over_5", "ast_rolling_avg_over_5", "opp_ast"
        ]
    },

    "pra": {
        "target": "pts_reb_ast",
        "features": [
            "is_home", "is_b2b", "min_rolling_avg_over_5", "pra_rolling_avg_over_5", "opp_fg_pct", "opp_pts", "opp_reb", "opp_ast"
        ]
    },

    "blocks": {
        "target": "blk",
        "features": [
            "is_home", "is_b2b", "min_rolling_avg_over_5", "blk_rolling_avg_over_5", "opp_blk"
        ]
    },

    "steals": {
        "target": "stl",
        "features": [
            "is_home", "is_b2b", "min_rolling_avg_over_5", "stl_rolling_avg_over_5", "opp_stl"
        ]
    },

    "threes": {
        "target": "three_pts_made",
        "features": [
            "is_home", "is_b2b", "min_rolling_avg_over_5", "threes_pct_rolling_avg_over_5", "threes_att_rolling_avg_over_5", "opp_fg3_pct", "opp_fg3_pct_rank", "opp_oreb"
        ]
    }
}

models = joblib.load("models.pkl")

future_df = pd.read_sql("SELECT * FROM next_game_features_mv", engine)

for stat, cfg in STAT_CONFIGS.items():
    future_df[f"predicted_{stat}"] = models[stat].predict(
        future_df[cfg["features"]]
    )