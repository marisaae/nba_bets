import plotly.graph_objects as go
import pandas as pd
from utils.data_load import load_player_stats
from utils.market_mappings import MARKET_TO_LAST_5
import streamlit as st

def get_last_5_stat(market, player_stats):
    col_name = MARKET_TO_LAST_5.get(market)

    if col_name is None or col_name not in player_stats.columns:
        return None
    
    return player_stats[["game_date", "matchup", col_name]].rename(
        columns={col_name: market}
    )

def render_prop_chart(player_id, prop_line, market, prediction):
    last_5_stats = load_player_stats(player_id, "2025-26").head(5)
    last_5_market_stats = get_last_5_stat(market, last_5_stats)

    max = last_5_market_stats[market].max()
    max_range = max + 1 if max >= prop_line else prop_line + 1

    diff = abs(prediction - prop_line)
    offset = 6
    if diff < .5:
        if prop_line > prediction:
            prop_yshift = offset
            pred_yshift = -offset
        else:
            prop_yshift = -offset
            pred_yshift = offset
    else:
        prop_yshift = 0
        pred_yshift = 0

    stats = last_5_market_stats[market]
    avg_stat = stats.mean().round(1)
    opp = last_5_market_stats["matchup"].str.split().str[-1]
    dates = pd.to_datetime(last_5_market_stats["game_date"]).dt.strftime("%m/%d")

    x_labels = [f"<b>{o}</b><br>{d}" for o, d in zip(opp, dates)]

    colors = ['red' if val < prop_line
              else 'gray' if val == prop_line 
              else 'green' 
              for val in stats]
    
    fig = go.Figure(
            [go.Bar(
                x=x_labels, 
                y=stats,
                marker_color=colors,
                meta=market,
                hovertemplate=("%{meta}: %{y}<extra></extra>"),
                texttemplate="%{y}",
                textposition="inside",
                textfont=dict(size=18)
                )
            ])
    
    fig.update_xaxes(title_text=f"<b>{avg_stat}</b> avg last 5",title_font_color="black", title_font_size=18,autorange="reversed", linecolor='black', linewidth=1, tickfont=dict(size=14))
    fig.update_yaxes(title_text=f"{market}", title_font_color="black", linecolor='black', linewidth=1, range=[0, max_range])

    fig.add_hline(
        y=prop_line,
        line_dash="dot",
        line_color="black"
    )

    last_x = x_labels[0]
    fig.add_annotation(
        x=last_x,
        y=prop_line,
        xref="x",
        yref="y",
        text=f"Prop Line: <b>{prop_line}</b>",
        showarrow=False,
        xanchor="left",
        yanchor="middle",
        yshift=prop_yshift,
        xshift=50,
        font=dict(size=14, color="black"),
        bgcolor="white"
    )

    fig.add_hline(
        y=prediction,
        line_dash="longdash",
        line_color="black"
    )
    fig.add_annotation(
        x=last_x,
        y=prediction,
        xref="x",
        yref="y",
        text=f"Prediction: <b>{prediction}</b>",
        showarrow=False,
        xanchor="left",
        yanchor="middle",
        xshift=50,
        yshift=pred_yshift,
        font=dict(size=14, color="black"),
        bgcolor="white"
    )

    fig.update_layout(
        title={
        'text': f"{market} Last 5 Games",
        'y': 0.9,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'size': 20, 'color': 'black'}
        },
        barcornerradius=15,
        height=600,
        width=600, 
        showlegend=False
        )
    return fig