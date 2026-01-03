import streamlit as st
from fetch_api.nba_fetch import fetch_all_teams
from utils.player_stats import render_player_list, render_player_page
from utils.data_format import format_schedule, highlight_lakers_score, highlight_preseason
from utils.data_load import load_team_schedule, load_team_roster, load_team_info, load_all_player_props, load_player_props

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

if "selected_prop_player" not in st.session_state:
    st.session_state.selected_prop_player = None

query_params = st.query_params

if "player_id" in query_params:
    st.session_state.selected_player = int(query_params["player_id"])
    st.session_state.page = "player"

all_teams = fetch_all_teams()

lal_team_abbrev = "LAL"
lal_team_id = all_teams.loc[all_teams['abbreviation'] == lal_team_abbrev, 'id'].iloc[0]
st.set_page_config(page_title="NBA Player Props", layout="wide")


team_df = load_team_info(lal_team_id)

standing = team_df["standing"].iloc[0].astype(str)
record = team_df["record"].iloc[0]

col1, col2 = st.columns([.5, 3])
with col1:
    st.image("lakers_logo.png", width=200) 

with col2:
    st.header("Los Angeles Lakers", anchor="home")
    st.write(f"Western Conference Standing: **{standing}**")
    st.write(f"Record: **{record}**")


schedule_df = load_team_schedule(lal_team_id)
schedule_df = format_schedule(schedule_df, lal_team_id, "Lakers")
styled_schedule_df = schedule_df.style.apply(highlight_lakers_score, axis=1).apply(highlight_preseason, axis=1)
roster_df = load_team_roster(lal_team_id)


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
                        "player_id": None,
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
        render_player_page(roster_df, st.session_state.selected_player)

def render_player_props(roster_df, player_id):
    player = roster_df.loc[roster_df['player_id'] == player_id].iloc[0]
    st.header(player["full_name"])

with t4:
    if st.session_state.selected_prop_player is None: 
        df = load_all_player_props()
        st.dataframe(df)
    # else:
    #     # insert render_player_props(df, st.session_state.selected_prop_player)
        
                    