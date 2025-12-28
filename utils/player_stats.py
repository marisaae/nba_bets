import streamlit as st
from pathlib import Path
from utils.data_load import load_player_stats
from utils.charts.pts_chart import render_pts_chart, render_pts_trend_chart

def select_player(player_id):
    st.session_state.selected_player = player_id
    st.session_state.page = "player"
    st.query_params["player_id"] = str(player_id)
    st.rerun()


def go_back():
    st.session_state.selected_player = None
    st.query_params.clear()


def show_player_page(player_id):
    st.button("← Back to Team", on_click=lambda: st.query_params.clear())
    st.write(f"Player ID: {player_id}")


def calc_ppg(player_stats_df):
    points = player_stats_df["pts"].sum()
    games = player_stats_df.shape[0]
    if games == 0:
        return 0
    return round(points / games, 1)


def calc_apg(player_stats_df):
    assists = player_stats_df["ast"].sum()
    games = player_stats_df.shape[0]
    if games == 0:
        return 0
    return round(assists / games, 1)


def calc_fgpct(player_stats_df):
    fgm = player_stats_df["fgm"].sum()
    fga = player_stats_df["fga"].sum()
    if fga == 0:
        return 0
    return round((fgm / fga) * 100, 1)


def calc_3ppct(player_stats_df):
    three_made = player_stats_df["three_pts_made"].sum()
    three_att = player_stats_df["three_pts_att"].sum()
    if three_att == 0:
        return 0
    return round((three_made / three_att) * 100, 1)



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


def render_player_page(roster_df, player_id):
    player = roster_df.loc[roster_df['player_id'] == player_id].iloc[0]
    image_path = Path("player_headshots") / f"{player_id}.png"
    player_stats = load_player_stats(player_id, "2025-26")

    st.button("← Back", on_click=go_back)

    col1, col2, col3, col4, col5, col6 = st.columns([1.5, 2, 1, 1, 1, 1])
    with col1:
        st.image(image_path, width='content') 

    with col2:
        st.header(player["full_name"])
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

    st.subheader("Season Stats")

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
                "fouls": "PF"
                 },
                 hide_index=True)
    st.subheader("Points Performance")

    pts_chart = render_pts_chart(player_stats, player_id)
    st.plotly_chart(pts_chart, width='stretch')

    pts_trend_chart = render_pts_trend_chart(player_stats, player_id)
    st.plotly_chart(pts_trend_chart, width='content')