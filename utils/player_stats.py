import streamlit as st
from pathlib import Path
from utils.data_load import load_player_stats
from utils.charts.pts_chart import render_pts_chart, render_pts_trend_chart
from utils.charts.shooting_chart import render_shooting_trend_chart
from utils.charts.playmaking_chart import render_playmaking_chart
from utils.calculations import calc_ppg, calc_apg, calc_fgpct, calc_3ppct

def select_player_stat(player_id):
    st.session_state.selected_player_id = player_id
    st.session_state.stats_view = "player"
    st.rerun()


def go_back_to_stats_list():
    st.session_state.selected_player_id = None
    st.session_state.stats_view = "list"


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
                    select_player_stat(player["player_id"])

                idx += 1


def render_player_page(roster_df, player_id):
    player = roster_df.loc[roster_df['player_id'] == player_id].iloc[0]
    image_path = Path("player_headshots") / f"{player_id}.png"
    player_stats = load_player_stats(player_id, "2025-26")

    st.button("← Back", on_click=go_back_to_stats_list)

    col1, col2, col3, col4, col5, col6 = st.columns([1.5, 2, 1, 1, 1, 1])
    with col1:
        st.image(image_path, width='content') 

    with col2:
        st.header(player["full_name"], anchor="player-overview")
        st.write(f"""
                 Position: {player['position']}
                 <br>
                 Jersey Number: {player['number']}
                 <br>
                 Height: {player['height']}
                 <br>
                 Weight: {player['weight']}
                 """, unsafe_allow_html=True)
    
    with col3:
        ppg = calc_ppg(player_stats)
        st.markdown('<div style="text-align: center; font-weight: bold; font-size: 16px; background-color: purple; color: white;">PPG</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: center; font-weight: bold; font-size: 40px;">{ppg}</div>', unsafe_allow_html=True)
    
    with col4:
        apg = calc_apg(player_stats)
        st.markdown('<div style="text-align: center; font-weight: bold; font-size: 16px; background-color: purple; color: white;">APG</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: center; font-weight: bold; font-size: 40px;">{apg}</div>', unsafe_allow_html=True)

    with col5:
        three_pct = calc_3ppct(player_stats)
        st.markdown('<div style="text-align: center; font-weight: bold; font-size: 16px; background-color: purple; color: white;">3P%</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: center; font-weight: bold; font-size: 40px;">{three_pct}</div>', unsafe_allow_html=True)

    with col6:
        fg_pct = calc_fgpct(player_stats)
        st.markdown('<div style="text-align: center; font-weight: bold; font-size: 16px; background-color: purple; color: white;">FG%</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: center; font-weight: bold; font-size: 40px;">{fg_pct}</div>', unsafe_allow_html=True)

    left, middle, right = st.columns(3)
    with left:
        st.markdown('<a style="display:block;" class="nav-link" href="#points-performance">Jump to Points Performance</a>', unsafe_allow_html=True)

    with middle:
        st.markdown('<a style="display:block;" class="nav-link" href="#shooting-performance">Jump to Shooting Performance</a>', unsafe_allow_html=True)

    with right:
        st.markdown('<a style="display:block;" class="nav-link" href="#playmaking">Jump to Playmaking</a>', unsafe_allow_html=True)

    st.subheader(":violet[Season Stats]", divider="yellow")

    st.dataframe(player_stats, 
                column_config={
                "player_id": None,
                "season": None,
                "game_date": "Date",
                "matchup": "Matchup",
                "wl": "RESULT",
                "min": "MIN",
                "pts": "PTS",
                "fgm": "FGM",
                "fga": "FGA",
                "fg_pct": st.column_config.NumberColumn("FG%", format="%.2f"),
                "three_pts_made": "3PM",
                "three_pts_att": "3PA",
                "three_pts_pct": st.column_config.NumberColumn("3P%", format="%.2f"),
                "ftm": "FTM",
                "fta": "FTA",
                "ft_pct": st.column_config.NumberColumn("FT%", format="%.2f"),
                "oreb": "OREB",
                "dreb": "DREB",
                "tot_reb": "REB",
                "ast": "AST",
                "stl": "STL",
                "blk": "BLK",
                "turnover": "TO",
                "fouls": "PF",
                "pts_reb_ast": "PRA"
                 },
                 hide_index=True)
    
    st.subheader(":violet[Points Performance]", divider="yellow")

    pts_chart = render_pts_chart(player_stats, player_id)
    st.plotly_chart(pts_chart, width='stretch')

    pts_trend_chart = render_pts_trend_chart(player_stats, player_id)
    st.plotly_chart(pts_trend_chart, width='content')

    st.markdown('<a class="nav-link" href="#home">Back to Top</a>', unsafe_allow_html=True)

    st.subheader(":violet[Shooting Performance]", divider="yellow")
    shooting_trends = render_shooting_trend_chart(player_stats, player_id)
    st.plotly_chart(shooting_trends, width='stretch')

    st.markdown('<a class="nav-link" href="#home">Back to Top</a>', unsafe_allow_html=True)

    st.subheader(":violet[Playmaking]", divider="yellow")
    playmaking_chart = render_playmaking_chart(player_stats, player_id)
    st.plotly_chart(playmaking_chart, width='stretch')
    st.markdown('<a class="nav-link" href="#home">Back to Top</a>', unsafe_allow_html=True)
    
