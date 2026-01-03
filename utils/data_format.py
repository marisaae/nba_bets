import pandas as pd

def format_schedule(df, team_id, team_name="Lakers"):
    df = df.copy()
    df['game_date'] = pd.to_datetime(df['game_date']).dt.strftime("%m/%d/%Y")

    df["Matchup"] = df.apply(
        lambda row: (
            f"{team_name} vs {row['away_team_name']}"
            if row["home_team_id"] == team_id
            else f"{team_name} @ {row['home_team_name']}"
        ),
        axis=1
    )
    df["Score"] = df.apply(
        lambda row: (
            f"{row['home_team_score']} - {row['away_team_score']}"
            if row["home_team_id"] == team_id
            else f"{row['away_team_score']} - {row['home_team_score']}"
        ),
        axis=1
    )
    df["Result"] = df.apply(
        lambda row: (
            "—"
            if row["game_status"] != "Final"
            else (
                "W"
                if (
                    (row["home_team_id"] == team_id and row["home_team_score"] > row["away_team_score"])
                    or
                    (row["away_team_id"] == team_id and row["away_team_score"] > row["home_team_score"])
                )
                else "L"
            )
        ),
        axis=1
    )
    df = df.drop(columns=["home_team_id", "away_team_id", "home_team_name", "away_team_name", "home_team_score", "away_team_score"])
    return df


def highlight_lakers_score(row):
    lal_score, opp_score = map(
        int,
        row["Score"].split("-")
    )

    styles = [""] * len(row)

    score_idx = row.index.get_loc("Score")

    if lal_score > opp_score:
        styles[score_idx] = "font-weight: bold; color: green"
    elif lal_score == opp_score:
        styles[score_idx] = "color: grey"
    else:
        styles[score_idx] = "color: red"

    return styles


def highlight_preseason(row):
    if row["game_label"] == "Preseason":
        return ["color: #B0B0B0"] * len(row)
    return [""] * len(row)


def consolidate_props(df):
    pivot_df = (
        df.pivot_table(
            index=[
                "event_id",
                "game_date",
                "player_id",
                "full_name",
                "market",
                "point"
            ],
            columns="outcome_name",
            values="price",
            aggfunc="first"
        )
        .reset_index()
    )

    return pivot_df