import pandas as pd
import joblib
from tabulate import tabulate
from pathlib import Path



BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_DIR = BASE_DIR / "models"

def load_models():
    if not MODEL_DIR.exists():
        raise FileNotFoundError(f"Models directory not found: {MODEL_DIR}")

    models = {}
    for file in MODEL_DIR.iterdir():
        if file.name.endswith(".pkl"):
            stat = file.name.replace("_ridge_model.pkl", "")
            models[stat] = joblib.load(file)
    
    return models


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
def predict_next_game(STAT_CONFIGS, future_game_df):
    models = load_models()

    df = future_game_df.copy()

    for stat, cfg in STAT_CONFIGS.items():
        df[f"predicted_{stat}"] = models[stat].predict(
            df[cfg["features"]]
        )
    # output_path = BASE_DIR / "outputs" / "predictions_preview.csv"
    # output_path.parent.mkdir(exist_ok=True)

    # df.to_csv(output_path, index=False)
    # print(f"Saved to {output_path}")

    return df


def log_prediction(prediction_df, cur):
    rows_to_insert = []

    df = prediction_df[[
    "full_name",
    "player_id",
    "game_id",
    "game_date",
    "predicted_points",
    "predicted_rebounds",
    "predicted_assists",
    "predicted_pra",
    "predicted_blocks",
    "predicted_steals",
    "predicted_threes",
    ]].copy()

    df["game_date"] = pd.to_datetime(df["game_date"])

    if not df.empty:
        for _, row in df.iterrows():
            player_name = row["full_name"]
            player_id = row["player_id"]
            game_id = row["game_id"]
            game_date = row["game_date"]
            pred_pts = row["predicted_points"]
            pred_rebs = row["predicted_rebounds"]
            pred_asts = row["predicted_assists"]
            pred_pra = row["predicted_pra"]
            pred_blks = row["predicted_blocks"]
            pred_stls = row["predicted_steals"]
            pred_threes = row["predicted_threes"]
        
            rows_to_insert.append((player_name, player_id, game_id, game_date, pred_pts, pred_rebs, pred_asts, pred_pra, pred_blks, pred_stls, pred_threes))
    else:
        print("No predictions to insert.")

    query = """
        INSERT INTO player_prediction_log (player_name, player_id, game_id, game_date, pred_pts, pred_rebs, pred_asts, pred_pra, pred_blks, pred_stls, pred_three)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (player_id, game_id) DO UPDATE SET
            pred_pts = EXCLUDED.pred_pts,
            pred_rebs = EXCLUDED.pred_rebs,
            pred_asts = EXCLUDED.pred_asts,
            pred_pra = EXCLUDED.pred_pra,
            pred_blks = EXCLUDED.pred_blks,
            pred_stls = EXCLUDED.pred_stls,
            pred_three = EXCLUDED.pred_three,
            last_updated = NOW();
        """
    cur.executemany(query, rows_to_insert)

    print("Successfully logged player predictions.")