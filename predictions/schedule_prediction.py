from predictions.predict_models import predict_next_game, log_prediction, STAT_CONFIGS
from datetime import date
import os
from sqlalchemy import create_engine
import pandas as pd
from db.connection import get_connection
from dotenv import load_dotenv

load_dotenv()

def run_predictions():
    dsn = os.getenv("SQLALCHEMY_URL")
    engine = create_engine(dsn, connect_args={"options": "-c client_encoding=UTF8"},)
    today = date.today()

    query = "SELECT * FROM future_games;"

    future_game_df = pd.read_sql(query, engine)
    future_game_df = future_game_df.fillna(0)
    prediction_df = predict_next_game(STAT_CONFIGS, future_game_df)
    print("successfully predicted next games")
    with get_connection() as conn:
        with conn.cursor() as cur:
            log_prediction(prediction_df, cur)
    
    print("date: ", today)

if __name__ == "__main__":
    run_predictions()

