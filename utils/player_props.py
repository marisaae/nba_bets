import streamlit as st
from pathlib import Path
from utils.data_format import consolidate_props


def select_player_prop(player_id):
    st.session_state.selected_player_prop = player_id
    st.session_state.page = "player"
    st.query_params["player_id"] = str(player_id)
    st.rerun()


def go_back():
    st.session_state.selected_player_prop = None
    st.query_params.clear()

def render_prop_list(market_df):
    images_folder = Path("player_headshots") 

    num_cols = 7
    idx = 0
    rows = market_df.shape[0] // num_cols + 1
    for r in range(rows):
        cols = st.columns(num_cols)
        for c in range(num_cols):
            if idx >= market_df.shape[0]:
                break
            player = market_df.iloc[idx]
            image_path = images_folder / f"{player['player_id']}.png"

            with cols[c]:

                if image_path.exists():
                    st.image(str(image_path))
                else: st.image("placeholder_headshot.png")
                
                st.markdown(
                    f"<div class='player-name'>{player['full_name']}</div><p class='prop-info'>Line: {player['point']}<br> Over: {player['Over']}<br> Under: {player['Under']}</p>",
                    unsafe_allow_html=True
                )

                if st.button(
                    "View More Info",
                    use_container_width=True,
                    key=f"prop_{player['player_id']}_{player['market']}"
                ):
                    select_player_prop(player["player_id"])

                idx += 1

def render_all_props_page(all_props_df):

    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    link_style = """
        <style>
        .nav-link {
            text-align: center;
            font-weight: bold;
            padding: 8px 0;
            font-size: 16px;
        }
        .nav-link:hover {
            color: #E8BC2A;
        }
        </style>
    """

    st.markdown(link_style, unsafe_allow_html=True)

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
    pts_df = all_props_df[all_props_df["market"] == "player_points"]
    pts_df = consolidate_props(pts_df)
    pts_df = pts_df.sort_values("full_name")
    render_prop_list(pts_df)
    st.markdown('<a class="nav-link" href="#home">Back to Top</a>', unsafe_allow_html=True)

    st.subheader(":violet[Rebounds]", divider="yellow")
    rebs_df = all_props_df[all_props_df["market"] == "player_rebounds"]
    rebs_df = consolidate_props(rebs_df)
    rebs_df = rebs_df.sort_values("full_name")
    render_prop_list(rebs_df)
    st.markdown('<a class="nav-link" href="#home">Back to Top</a>', unsafe_allow_html=True)
    
    st.subheader(":violet[Assists]", divider="yellow")
    asts_df = all_props_df[all_props_df["market"] == "player_assists"]
    asts_df = consolidate_props(asts_df)
    asts_df = asts_df.sort_values("full_name")
    render_prop_list(asts_df)
    st.markdown('<a class="nav-link" href="#home">Back to Top</a>', unsafe_allow_html=True)

    st.subheader(":violet[Pts+Rebs+Asts]", divider="yellow")
    pra_df = all_props_df[all_props_df["market"] == "player_points_rebounds_assists"]
    pra_df = consolidate_props(pra_df)
    pra_df = pra_df.sort_values("full_name")
    render_prop_list(pra_df)
    st.markdown('<a class="nav-link" href="#home">Back to Top</a>', unsafe_allow_html=True)

    st.subheader(":violet[3-PT Made]", divider="yellow")
    thr_df = all_props_df[all_props_df["market"] == "player_threes"]
    thr_df = consolidate_props(thr_df)
    thr_df = thr_df.sort_values("full_name")
    render_prop_list(thr_df)
    st.markdown('<a class="nav-link" href="#home">Back to Top</a>', unsafe_allow_html=True)

    st.subheader(":violet[Steals]", divider="yellow")
    stl_df = all_props_df[all_props_df["market"] == "player_steals"]
    stl_df = consolidate_props(stl_df)
    stl_df = stl_df.sort_values("full_name")
    render_prop_list(stl_df)
    st.markdown('<a class="nav-link" href="#home">Back to Top</a>', unsafe_allow_html=True)

    st.subheader(":violet[Blocks]", divider="yellow")
    blk_df = all_props_df[all_props_df["market"] == "player_blocks"]
    blk_df = consolidate_props(blk_df)
    blk_df = blk_df.sort_values("full_name")
    render_prop_list(blk_df)
    st.markdown('<a class="nav-link" href="#home">Back to Top</a>', unsafe_allow_html=True)


def render_player_props_page(event_id, player_id):
    return