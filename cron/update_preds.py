import os
import pandas as pd
from datetime import date
from dotenv import load_dotenv
from sqlalchemy import create_engine
from predictions.predict_models import predict_next_game, log_prediction, STAT_CONFIGS
from db.connection import get_connection

load_dotenv()

def run_predictions():
    dsn = os.getenv("SQLALCHEMY_URL")
    engine = create_engine(dsn)
    today = date.today()

    query = "SELECT * FROM future_games;"

    future_game_df = pd.read_sql(query, engine)
    future_game_df = future_game_df.fillna(0)
    prediction_df = predict_next_game(STAT_CONFIGS, future_game_df)

    with get_connection() as conn:
        with conn.cursor() as cur:
            log_prediction(prediction_df, cur)
    
    print("date: ", today)

if __name__ == "__main__":
    run_predictions()

