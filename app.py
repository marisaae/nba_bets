import streamlit as st
from db.queries import get_team_info, get_team_schedule, get_team_roster
from fetch_api.nba_fetch import fetch_all_teams
import pandas as pd

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "team"  # default page
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Roster"
if "selected_player" not in st.session_state:
    st.session_state.selected_player = None

all_teams = fetch_all_teams()

lal_team_abbrev = "LAL"
lal_team_id = all_teams.loc[all_teams['abbreviation'] == lal_team_abbrev, 'id'].iloc[0]
st.set_page_config(page_title="NBA Player Props", layout="wide")

#@st.cache_data(ttl=3600)
def load_team_info(team_id):
    df = get_team_info(team_id)
    return df

team_df = load_team_info(lal_team_id)

standing = team_df["standing"].iloc[0].astype(str)
record = team_df["record"].iloc[0]

col1, col2 = st.columns([.5, 3])
with col1:
    st.image("lakers_logo.png", width=200) 

with col2:
    st.header("Los Angeles Lakers")
    st.write(f"Western Conference Standing: **{standing}**")
    st.write(f"Record: **{record}**")

def show_player_page(player_id):
    st.button("← Back to Team", on_click=lambda: st.query_params.clear())
    st.write(f"Player ID: {player_id}")

def load_team_schedule(team_id):
    df = get_team_schedule(team_id)
    return df

def load_team_roster(team_id):
    df = get_team_roster(team_id)
    return df

def format_schedule(df, team_id, team_name="Lakers"):
    df = df.copy()
    df['game_date'] = pd.to_datetime(df['game_date']).dt.strftime("%m-%d-%Y")

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

schedule_df = load_team_schedule(lal_team_id)
roster_df = load_team_roster(lal_team_id)
schedule_df = format_schedule(schedule_df, lal_team_id, "Lakers")
styled_schedule_df = schedule_df.style.apply(highlight_lakers_score, axis=1)


t1, t2, t3, t4 = st.tabs(["Schedule", "Roster", "Player Stats", "Player Props"])

if not schedule_df.empty:
    t1.subheader("Team Schedule")
    t1.dataframe(styled_schedule_df, 
                 column_config= {
                     "game_label": "Game Type",
                     "game_date": "Date",
                     "season_year": "Season",
                     "game_status": "Status",
                     "arena_name": "Arena"
                 },
                 hide_index=True)
else:
    t1.warning("Schedule data not found.")

if not roster_df.empty:
    t2.subheader("Team Roster")
    t2.dataframe(roster_df, 
                 column_config= {
                    "full_name": "Name",
                    "age": {
                            "label": "Age",
                            "alignment": "left",
                        },
                    "position": "Position",
                    "number": {
                            "label": "Jersey Number",
                            "alignment": "left",
                        },
                    "height": "Height",
                    "weight": "Weight"
                 },
                 hide_index=True)
    
t3.subheader("Click a player to view their stats")
t3.image("https://cdn.nba.com/headshots/nba/latest/1040x760/1642876.png", width=200)
                 
# # need to show a general team page with the general team info and stats
# # need to have player profiles with their current season stats
#     # this needs to have visualizations showing their stats for the whole season on a graph
# # need to have player odds profiles with their current / next game bets if available and show visualizations of the last 5 game stats and have a line of the current projected stats along with the model to say what their prediction is for the next game stats
