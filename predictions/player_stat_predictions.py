import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
import os
from dotenv import load_dotenv
from tabulate import tabulate

pd.set_option("display.max_columns", None)


load_dotenv()
dsn = os.getenv("SQLALCHEMY_URL")
engine = create_engine(dsn)

query_model = "SELECT * FROM model_player_stats;"
query_def = "SELECT * FROM team_def_stats;"

model_stats_df = pd.read_sql(query_model, engine)
def_stats_df = pd.read_sql(query_def, engine)

model_stats_df["primary_position"] = model_stats_df["position"].str.split("-").str[0]
model_stats_df = model_stats_df.drop(columns=["position"])

merged_model_stats = model_stats_df.merge(
    def_stats_df,
    left_on=["opp_team_id", "primary_position", "season"],
    right_on=["team_id", "opp_player_position", "season"],
    how="left"
)

merged_model_stats = merged_model_stats.drop(columns=["opp_team_id", "team_id", "team_name", "gp", "opp_player_position", "last_updated"])
merged_model_stats = merged_model_stats.rename(columns={"win_pct": "opp_wins_pct"})
merged_model_stats = merged_model_stats.fillna(0)

print(tabulate(merged_model_stats,headers='keys', tablefmt='fancy_grid'))

players = merged_model_stats["full_name"].unique()

train_players, test_players = train_test_split(players, test_size=0.2, random_state=42)

train_df = merged_model_stats[merged_model_stats["full_name"].isin(train_players)]
test_df = merged_model_stats[merged_model_stats["full_name"].isin(test_players)]

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

models = {}
metrics = {}

# for stat, cfg in STAT_CONFIGS.items():
#     X = merged_model_stats[cfg["features"]]
#     y = merged_model_stats[cfg["target"]]

#     X_train = train_df[cfg["features"]]
#     y_train = train_df[cfg["target"]].astype(float)

#     X_test = test_df[cfg["features"]]
#     y_test = test_df[cfg["target"]].astype(float)

#     model = Ridge(alpha=1.0)
#     model.fit(X_train, y_train)

#     test_preds = model.predict(X_test)

#     models[stat] = model

#     metrics[stat] = {
#         "MAE": mean_absolute_error(y_test, test_preds),
#         "R2": r2_score(y_test, test_preds),
#     }

#     print(f"\n=== {stat.upper()} MODEL ===")
#     print("MAE:", round(metrics[stat]["MAE"], 2))
#     print("R² :", round(metrics[stat]["R2"], 2))

# for stat, cfg in STAT_CONFIGS.items():
#     merged_model_stats[f"predicted_{stat}"] = models[stat].predict(
#         merged_model_stats[cfg["features"]]
#     )

# results = merged_model_stats[[
#     "full_name", "game_date",
#     "pts", "predicted_points",
#     "tot_reb", "predicted_rebounds",
#     "ast", "predicted_assists",
#     "pts_reb_ast", "predicted_pra",
#     "blk", "predicted_blocks",
#     "stl", "predicted_steals",
#     "three_pts_made", "predicted_threes"
# ]].sort_values(["full_name", "game_date"])

# print(results.head(50))