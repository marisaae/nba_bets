import plotly.graph_objects as go
from plotly.subplots import make_subplots

def render_pts_chart(player_stats_df, player_id):
    player_data = player_stats_df[player_stats_df["player_id"] == player_id]
    avg_points = player_data["pts"].mean().round(1)
    min_pts = player_data["pts"].min()
    max_pts = player_data["pts"].max()
    home_pts = player_data[player_data["matchup"].str.contains(" vs. ")]["pts"]
    home_pts_avg = home_pts.mean().round(1)
    home_game_dates = player_data[player_data["matchup"].str.contains(" vs. ")]["game_date"]
    away_pts = player_data[player_data["matchup"].str.contains(" @ ")]["pts"]
    away_pts_avg = away_pts.mean().round(1)
    away_game_dates = player_data[player_data["matchup"].str.contains(" @ ")]["game_date"]

    fig = make_subplots(rows=2, cols=2,
                        specs=[
                            [{}, {"rowspan": 2}],
                            [{}, None]
                        ], 
                        vertical_spacing=0.35,
                        subplot_titles=("Home Points Scored", "Home vs. Away Avg Points", "Away Points Scored"))

    fig.add_trace(go.Scatter(
        x=home_game_dates,
        y=home_pts,
        name="Home Points",
        line=dict(color='purple')
    ), row=1, col=1)

    fig.update_xaxes(title_text="Game Date", title_font_color="black",row=1, col=1, autorange="reversed", tickangle=45, linecolor='black', linewidth=1)
    fig.update_yaxes(title_text="Points Scored", title_font_color="black",row=1, col=1, linecolor='black', linewidth=1, range=[min_pts-5, max_pts + 5])

    fig.add_trace(go.Scatter(
        x=away_game_dates,
        y=away_pts,
        name="Away Points",
        line=dict(color='gold')
    ), row=2, col=1)

    fig.update_xaxes(title_text="Game Date", title_font_color="black", row=2, col=1, autorange="reversed", tickangle=45, linecolor='black', linewidth=1)
    fig.update_yaxes(title_text="Points Scored", title_font_color="black", row=2, col=1, linecolor='black', linewidth=1, range=[min_pts-5, max_pts + 5])

    fig.add_trace(go.Bar(
        x=["Home Avg", "Away Avg"],
        y=[home_pts_avg, away_pts_avg],
        marker_color=['purple', 'gold'],
        text=[f"{home_pts_avg:.1f}", f"{away_pts_avg:.1f}"],
        textposition='auto'
    ), row=1, col=2
    )
    fig.update_xaxes(title_font_color="black", row=1, col=2, tickangle=45, linecolor='black', linewidth=1)
    fig.update_yaxes(title_font_color="black", row=1, col=2, linecolor='black', linewidth=1)

    fig.update_layout(height=600,
                      showlegend=False)
    
    fig.update_annotations(font=dict(size=20, weight="bold", color="black"))

    fig.add_hline(
    y=avg_points,
    line_dash="dot",
    line_color="grey",
    annotation_text="Season Avg",
    annotation_position="top right"
    )

    return fig


def render_pts_trend_chart(player_stats_df, player_id):
    player_data = player_stats_df[player_stats_df["player_id"] == player_id]
    avg_points = player_data["pts"].mean().round(1)
    game_count = player_data.shape[0]
    mid = game_count // 2

    first_half = player_data.iloc[:mid]
    second_half = player_data.iloc[mid:]

    avg_first_half = first_half["pts"].mean().round(1)
    avg_second_half = second_half["pts"].mean().round(1)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=["Early Games", "Recent Games"],
        y=[avg_first_half, avg_second_half],
        name="Points per Game",
        marker_color=["purple", "gold"],
    ))
    fig.update_xaxes(title_font_color="black", linecolor='black', linewidth=1)
    fig.update_yaxes(title_text="Points per Game", title_font_color="black", linecolor='black', linewidth=1)

    fig.update_layout(
        title={
        'text': f"Performance Trend (First {mid} vs Last {game_count - mid} Games)",
        'y': 0.9,       # Vertical position (0 to 1)
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'size': 20, 'color': 'black'}
        },
        height=600,
        width=600
    )

    fig.add_hline(
        y=avg_points,
        line_dash="dot",
        line_color="grey",
        annotation_text="Season Avg",
        annotation_position="top right"
        )

    return fig