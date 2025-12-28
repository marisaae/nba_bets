import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.calculations import calc_apg

# assists per game and assists home vs away
def render_playmaking_chart(player_stats_df, player_id):
    player_data = player_stats_df[player_stats_df["player_id"] == player_id].head(10)
    avg_ast = calc_apg(player_data)
    min_ast = player_data["ast"].min()
    max_ast = player_data["ast"].max()
    home_ast = player_data[player_data["matchup"].str.contains(" vs. ")]["ast"]
    home_ast_avg = home_ast.mean().round(1)
    away_ast = player_data[player_data["matchup"].str.contains(" @ ")]["ast"]
    away_ast_avg = away_ast.mean().round(1)

    fig = make_subplots(rows=1, cols=2, subplot_titles=("Assists per Last 10 Games", "Season Assists Home vs Away"))

    fig.add_trace(go.Scatter(
        x=player_data['game_date'],
        y=player_data['ast'],
        name="Assists",
        line=dict(color='purple'),
        hovertemplate="Assists: %{y}<br>Date: %{x}<extra></extra>"
    ), row=1, col=1)

    fig.update_xaxes(title_text="Game Date", title_font_color="black",row=1, col=1, autorange="reversed", tickangle=45, linecolor='black', linewidth=1)
    fig.update_yaxes(title_text="Assists", title_font_color="black",row=1, col=1, linecolor='black', linewidth=1, range=[min_ast-5, max_ast + 5])

    fig.add_trace(go.Bar(
        x=["Home Avg", "Away Avg"],
        y=[home_ast_avg, away_ast_avg],
        marker_color=['purple', 'gold'],
        text=[f"{home_ast_avg:.1f}", f"{away_ast_avg:.1f}"],
        textfont=dict(size=18),
        textposition='inside',
        insidetextanchor='middle',
        hoverinfo="skip"
    ), row=1, col=2
    )

    fig.update_xaxes(title_font_color="black", row=1, col=2, linecolor='black', linewidth=1)
    fig.update_yaxes(title_font_color="black", row=1, col=2, linecolor='black', linewidth=1)

    fig.update_annotations(font=dict(size=20, weight="bold", color="black"))

    fig.add_hline(
        y=avg_ast,
        line_dash="dot",
        line_color="grey",
        annotation_text=f"Season Avg: {avg_ast}",
        annotation_position="top right"
    )

    fig.update_layout(height=600, showlegend=False)
    return fig