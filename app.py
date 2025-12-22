import streamlit as st
from db.queries import get_team_info, get_team_schedule, get_team_roster, get_player_stats
from fetch_api.nba_fetch import fetch_all_teams
import pandas as pd
from pathlib import Path

st.markdown("""
<style>
[data-testid="stImage"] {
    text-align: center;
    display: block;
    margin-left: auto;
    margin-right: auto;
    margin-top: 20px;
    width: 100%;
    border: 2px solid purple;
}
.player-name {
    font-size: 1.05rem;
    font-weight: 600;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)

# Initialize session state
if "selected_player" not in st.session_state:
    st.session_state.selected_player = None


# helper functions
def select_player(player_id):
    st.session_state.selected_player = player_id
    st.session_state.page = "player"
    st.query_params["player_id"] = str(player_id)
    st.rerun()


def go_back():
    st.session_state.selected_player = None
    st.query_params.clear()


def render_player_page(player_id):
    st.button("← Back", on_click=go_back)

    st.header("Player Stats")
    st.write(f"Player ID: {player_id}")

    st.dataframe(load_player_stats(player_id, "2025-26"), hide_index=True)


def show_player_page(player_id):
    st.button("← Back to Team", on_click=lambda: st.query_params.clear())
    st.write(f"Player ID: {player_id}")


def load_team_schedule(team_id):
    df = get_team_schedule(team_id)
    return df


def load_team_roster(team_id):
    df = get_team_roster(team_id)
    return df

def load_player_stats(player_id, curr_season):
    df = get_player_stats(player_id, curr_season)
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


def render_player_list(roster_df):
    
    roster_df_sorted = roster_df.sort_values(by="full_name")
    images_folder = Path("player_headshots") 

    num_cols = 5
    rows = roster_df_sorted.shape[0] // num_cols + 1
    idx = 0

    st.subheader("Click a player to view their stats")

    for r in range(rows):
        cols = st.columns(num_cols)
        for c in range(num_cols):
            if idx >= roster_df_sorted.shape[0]:
                break
            player = roster_df_sorted.iloc[idx]
            image_path = images_folder / f"{player['player_id']}.png"

            with cols[c]:

                if image_path.exists():
                    st.image(str(image_path))
                else: st.image("placeholder_headshot.png")
                
                st.markdown(
                    f"<div class='player-name'>{player['full_name']}</div>",
                    unsafe_allow_html=True
                )

                if st.button(
                    "View Stats",
                    width="stretch",
                    key=f"player_{player['player_id']}"
                ):
                    select_player(player["player_id"])

                idx += 1


query_params = st.query_params

if "player_id" in query_params:
    st.session_state.selected_player = int(query_params["player_id"])
    st.session_state.page = "player"

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


schedule_df = load_team_schedule(lal_team_id)
roster_df = load_team_roster(lal_team_id)
schedule_df = format_schedule(schedule_df, lal_team_id, "Lakers")
styled_schedule_df = schedule_df.style.apply(highlight_lakers_score, axis=1)


t1, t2, t3, t4 = st.tabs(["Schedule", "Roster", "Player Stats", "Player Props"])

with t1:
    if not schedule_df.empty:
        st.subheader("Team Schedule")
        st.dataframe(
            styled_schedule_df,
            column_config={
                "game_label": "Game Type",
                "game_date": "Date",
                "season_year": "Season",
                "game_status": "Status",
                "arena_name": "Arena"
            },
            hide_index=True
        )
    else:
        st.warning("Schedule data not found.")

with t2:
    if not roster_df.empty:
        st.subheader("Team Roster")
        st.dataframe(roster_df, 
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
    else: st.warning("Roster data not found.")

with t3:
    if st.session_state.selected_player is None:
        render_player_list(roster_df)
    else:
        render_player_page(st.session_state.selected_player)


                    