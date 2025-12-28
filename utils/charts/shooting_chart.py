import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.calculations import calc_3ppct, calc_mid, calc_fgpct

def render_shooting_trend_chart(player_stats_df, player_id):
    player_data = player_stats_df[player_stats_df["player_id"] == player_id]
    avg_3p_pct = calc_3ppct(player_data) / 100
    avg_fg_pct = calc_fgpct(player_data) / 100

    game_count, mid = calc_mid(player_data)
    first_half = player_data.iloc[:mid]
    second_half = player_data.iloc[mid:]

    avg_fg_pct_first_half = calc_fgpct(first_half) / 100
    avg_fg_pct_second_half = calc_fgpct(second_half) / 100

    avg_3ppct_first_half = calc_3ppct(first_half) / 100
    avg_3ppct_second_half = calc_3ppct(second_half) / 100

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=(f"FG% Trend (First {mid} vs Last {game_count - mid} Games)", f"3P% Trend (First {mid} vs Last {game_count - mid} Games)"))

    fig.add_trace(go.Bar(
            x=["Early Games", "Recent Games"],
            y=[avg_fg_pct_first_half, avg_fg_pct_second_half],
            name="FG% per Game",
            marker_color=["purple", "gold"],
            text=[f"{avg_fg_pct_first_half * 100:.1f}", f"{avg_fg_pct_second_half * 100:.1f}"],
            textfont=dict(size=18),
            textposition='inside',
            insidetextanchor='middle',
            hoverinfo="skip"
        ), row=1, col=1)

    fig.update_yaxes(title_text="FG% per Game", title_font_color="black", linecolor='black', linewidth=1, tickformat='.0%', row=1, col=1)


    fig.add_trace(go.Bar(
        x=["Early Games", "Recent Games"],
        y=[avg_3ppct_first_half, avg_3ppct_second_half],
        name="3P% per Game",
        marker_color=["purple", "gold"],
        text=[f"{avg_3ppct_first_half * 100:.1f}", f"{avg_3ppct_second_half * 100:.1f}"],
        textfont=dict(size=18),
        textposition='inside',
        insidetextanchor='middle',
        hoverinfo="skip"
    ), row=1, col=2)

    fig.update_xaxes(title_font_color="black", linecolor='black', linewidth=1)
    fig.update_yaxes(title_text="3P% per Game", title_font_color="black", linecolor='black', linewidth=1, tickformat='.0%', row=1, col=2)

    fig.update_annotations(font=dict(size=20, weight="bold", color="black"))

    fig.add_hline(
        y=avg_fg_pct,
        line_dash="dot",
        line_color="grey",
        annotation_text=f"Season Avg: {avg_fg_pct * 100}%",
        annotation_position="top right",
        row=1,
        col=1
        )
    
    fig.add_hline(
        y=avg_3p_pct,
        line_dash="dot",
        line_color="grey",
        annotation_text=f"Season Avg: {avg_3p_pct * 100}%",
        annotation_position="top right",
        row=1,
        col=2
        )


    fig.update_layout(
        showlegend=False,
        height=600
    )


    return fig