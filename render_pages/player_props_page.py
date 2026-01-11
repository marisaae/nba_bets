import streamlit as st
import pandas as pd
import math
from pathlib import Path
from utils.data_format import consolidate_props, format_prop_market
from utils.data_load import load_rolling_avg_stats, load_player_prediction
from utils.charts.props_chart import render_prop_chart
from utils.market_mappings import MARKET_TO_ROLLING_COL


def select_player_prop(player_id, market):
    st.session_state.selected_prop_player_id = player_id
    st.session_state.selected_prop_market = market
    st.session_state.props_view = "player"
    st.rerun()


def go_back_to_props_list():
    st.session_state.selected_prop_player_id = None
    st.session_state.selected_prop_market = None
    st.session_state.props_view = "list"


def get_rolling_avg_market(market, player_row):
    col_name = MARKET_TO_ROLLING_COL.get(market)

    if col_name is None or col_name not in player_row.columns:
        return None

    value = player_row.iloc[0][col_name]

    return value


def render_market_prop_list(market_df):
    images_folder = Path("player_headshots")
    placeholder_image = images_folder / "placeholder.png" 

    num_cols = 7
    idx = 0
    rows = math.ceil(market_df.shape[0] / num_cols)
    for r in range(rows):
        cols = st.columns(num_cols)
        for c in range(num_cols):
            if idx >= market_df.shape[0]:
                break
            player = market_df.iloc[idx]
            player_id = int(player['player_id'])
            player_image = images_folder / f"{player_id}.png"

            with cols[c]:
                if player_image.exists():
                    st.image(str(player_image))
                else:
                    st.image(str(placeholder_image))
                
                st.markdown(
                    f"<div class='player-name'>{player['full_name']}</div><p class='prop-info'><b><span style='color:red;''>Line: {player['point']}</span></b><br> Over: {player['Over']}<br> Under: {player['Under']}</p>",
                    unsafe_allow_html=True
                )

                if st.button(
                    "View More Info",
                    use_container_width=True,
                    key=f"props_{player_id}_{player['market']}"
                ):
                    select_player_prop(
                        player_id=player_id,
                        market=player["market"]
                    )

                idx += 1


def render_player_prop_list(player_prop_df):
    num_cols = 7
    idx = 0
    rows = player_prop_df.shape[0] // num_cols + 1
    # loop through player_prop df to print each prop in a column
    for r in range(rows):
        cols = st.columns(num_cols)
        for c in range(num_cols):
            if idx >= player_prop_df.shape[0]:
                break
            market_prop = player_prop_df.iloc[idx]
            player_id = market_prop["player_id"]

            with cols[c]:
                market_name = format_prop_market(market_prop["market"])                
                st.markdown(
                    f"<div class='market-name'>{market_name}</div><p class='prop-info'><b><span style='color:red;''>Line: {market_prop['point']}</span></b><br> Over: {market_prop['Over']}<br> Under: {market_prop['Under']}</p>",
                    unsafe_allow_html=True
                )

                if st.button(
                    "View More Info",
                    use_container_width=True,
                    key=f"props_more_{player_id}_{market_prop['market']}"
                ):
                    select_player_prop(
                        player_id=player_id,
                        market=market_prop["market"]
                    )

                idx += 1


def render_more_props(player_id, all_props_df):
    player_props = all_props_df.loc[all_props_df["player_id"] == player_id]
    player_name = player_props["full_name"].iloc[0]
    player_props = consolidate_props(player_props)
    st.subheader(f"All props for {player_name} for the next game")
    render_player_prop_list(player_props)


def render_all_props_page(all_props_df):

    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

    with col1:
        st.markdown('<a style="display:block;" class="nav-link" href="#points">Jump to Points</a>', unsafe_allow_html=True)

    with col2:
        st.markdown('<a style="display:block;" class="nav-link" href="#rebounds">Jump to Rebounds</a>', unsafe_allow_html=True)

    with col3:
        st.markdown('<a style="display:block;" class="nav-link" href="#assists">Jump to Assists</a>', unsafe_allow_html=True)

    with col4:
        st.markdown('<a style="display:block;" class="nav-link" href="#pts-rebs-asts">Jump to Pts+Rebs+Ast</a>', unsafe_allow_html=True)

    with col5:
        st.markdown('<a style="display:block;" class="nav-link" href="#3-pt-made">Jump to 3PT-Made</a>', unsafe_allow_html=True)

    with col6:
        st.markdown('<a style="display:block;" class="nav-link" href="#steals">Jump to Steals</a>', unsafe_allow_html=True)

    with col7:
        st.markdown('<a style="display:block;" class="nav-link" href="#blocks">Jump to Blocks</a>', unsafe_allow_html=True)


    st.subheader(":violet[Points]", divider="yellow")
        # 🔍 TEMP DEBUG — REMOVE AFTER
    luka_debug = all_props_df[all_props_df["player_id"] == 1629028]
    st.write("Luka raw rows:", luka_debug)

    pts_df = all_props_df[all_props_df["market"] == "player_points"]
    pts_df = consolidate_props(pts_df)

    # 🔍 TEMP DEBUG — REMOVE AFTER
    luka_after = pts_df[pts_df["player_id"] == 1629028]
    st.write("Luka after consolidate:", luka_after)
    
    pts_df = all_props_df[all_props_df["market"] == "player_points"]
    pts_df = consolidate_props(pts_df)
    pts_df = pts_df.sort_values("full_name")
    render_market_prop_list(pts_df)
    st.markdown('<a class="nav-link" href="#home">Back to Top</a>', unsafe_allow_html=True)

    st.subheader(":violet[Rebounds]", divider="yellow")
    rebs_df = all_props_df[all_props_df["market"] == "player_rebounds"]
    rebs_df = consolidate_props(rebs_df)
    rebs_df = rebs_df.sort_values("full_name")
    render_market_prop_list(rebs_df)
    st.markdown('<a class="nav-link" href="#home">Back to Top</a>', unsafe_allow_html=True)
    
    st.subheader(":violet[Assists]", divider="yellow")
    asts_df = all_props_df[all_props_df["market"] == "player_assists"]
    asts_df = consolidate_props(asts_df)
    asts_df = asts_df.sort_values("full_name")
    render_market_prop_list(asts_df)
    st.markdown('<a class="nav-link" href="#home">Back to Top</a>', unsafe_allow_html=True)

    st.subheader(":violet[Pts+Rebs+Asts]", divider="yellow")
    pra_df = all_props_df[all_props_df["market"] == "player_points_rebounds_assists"]
    pra_df = consolidate_props(pra_df)
    pra_df = pra_df.sort_values("full_name")
    render_market_prop_list(pra_df)
    st.markdown('<a class="nav-link" href="#home">Back to Top</a>', unsafe_allow_html=True)

    st.subheader(":violet[3-PT Made]", divider="yellow")
    thr_df = all_props_df[all_props_df["market"] == "player_threes"]
    thr_df = consolidate_props(thr_df)
    thr_df = thr_df.sort_values("full_name")
    render_market_prop_list(thr_df)
    st.markdown('<a class="nav-link" href="#home">Back to Top</a>', unsafe_allow_html=True)

    st.subheader(":violet[Steals]", divider="yellow")
    stl_df = all_props_df[all_props_df["market"] == "player_steals"]
    stl_df = consolidate_props(stl_df)
    stl_df = stl_df.sort_values("full_name")
    render_market_prop_list(stl_df)
    st.markdown('<a class="nav-link" href="#home">Back to Top</a>', unsafe_allow_html=True)

    st.subheader(":violet[Blocks]", divider="yellow")
    blk_df = all_props_df[all_props_df["market"] == "player_blocks"]
    blk_df = consolidate_props(blk_df)
    blk_df = blk_df.sort_values("full_name")
    render_market_prop_list(blk_df)
    st.markdown('<a class="nav-link" href="#home">Back to Top</a>', unsafe_allow_html=True)


def render_player_props_page(all_props_df, roster_df, player_id, prop_market, event_id):
    st.button(
    "← Back",
    key=f"back_props_{st.session_state.selected_prop_player_id}_{st.session_state.selected_prop_market}",
    on_click=go_back_to_props_list
    )

    player_props = all_props_df[(all_props_df["player_id"]==player_id) & (all_props_df["market"] == prop_market) & (all_props_df["event_id"]== event_id)]

    player_props = consolidate_props(player_props)
    game_date = pd.to_datetime(player_props["game_date"].iloc[0]).strftime("%m/%d/%Y")
    game_time = player_props["game_status"].iloc[0]
    market = format_prop_market(prop_market)

    player_rolling_stats_row = load_rolling_avg_stats(player_id)

    player = roster_df.loc[roster_df['player_id'] == player_id].iloc[0]
    image_path = Path("player_headshots") / f"{player_id}.png"

    st.subheader(f"{market} prop for next game on {game_date} at {game_time}", anchor="top")
    col1, col2, col3, col4, col5, col6, col7 = st.columns([1.5, 1, 1, 1, 1, 1, 1])
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
        line = player_props["point"].iloc[0]
        st.markdown('<div style="text-align: center; font-weight: bold; font-size: 16px; background-color: red; color: white;">Prop Line</div>', unsafe_allow_html=True)
        st.markdown(f'''
                    <div style="text-align: center;">
                    <span style="font-weight: bold; font-size: 40px;">{line}</span> {market}</div>
                     ''', unsafe_allow_html=True)
        
    with col4:
        line = player_props["point"].iloc[0]
        prediction = load_player_prediction(player_id, market)
        st.markdown('<div style="text-align: center; font-weight: bold; font-size: 16px; background-color: yellow; color: black;">Prediction</div>', unsafe_allow_html=True)
        st.markdown(f'''
                    <div style="text-align: center;">
                    <span style="font-weight: bold; font-size: 40px;">{prediction}</span> {market}</div>
                     ''', unsafe_allow_html=True)

    with col5:
        last_5_avg = get_rolling_avg_market(market, player_rolling_stats_row)
        st.markdown(f'<div style="text-align: center; font-weight: bold; font-size: 16px; background-color: purple; color: white;">Last 5 Avg.</div>', unsafe_allow_html=True)
        st.markdown(f'''
                    <div style="text-align: center;">
                    <span style="font-weight: bold; font-size: 40px;">{last_5_avg}</span> {market}</div>
                    ''', unsafe_allow_html=True)

    with col6:
        over = player_props["Over"].iloc[0]
        st.markdown('<div style="text-align: center; font-weight: bold; font-size: 16px; background-color: purple; color: white;">Over</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: center; font-weight: bold; font-size: 40px;">{over}</div>', unsafe_allow_html=True)
   
    with col7:
        under = player_props["Under"].iloc[0]
        st.markdown('<div style="text-align: center; font-weight: bold; font-size: 16px; background-color: purple; color: white;">Under</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: center; font-weight: bold; font-size: 40px;">{under}</div>', unsafe_allow_html=True)


    prop_chart = render_prop_chart(player_id, line, market, prediction)
    st.plotly_chart(prop_chart, width="content")
    
    render_more_props(st.session_state.selected_prop_player_id, all_props_df)
    st.markdown('<a class="nav-link" href="#top">Back to Top</a>', unsafe_allow_html=True)
